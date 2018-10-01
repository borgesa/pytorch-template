import datetime
import json
import os
import math
import logging
# Third party imports:
import torch
# Local imports
from model.model_utils import get_optimizer

from utils.util import ensure_dir
from utils.visualization import WriterTensorboardX


class BaseTrainer:
    """
    Base class for all trainers
    """
    def __init__(self, model, loss, metrics, resume, config, train_logger=None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        self.model = model
        self.loss = loss
        self.metrics = metrics
        self.name = config['name']
        self.epochs = config['trainer']['epochs']
        self.save_freq = config['trainer']['save_freq']
        self.verbosity = config['trainer']['verbosity']

        # CUDA settings:
        self.with_cuda = config['cuda'] and torch.cuda.is_available()
        if config['cuda'] and not torch.cuda.is_available():
            self.logger.warning('Warning: There\'s no CUDA support on this machine, '
                                'training is performed on CPU.')
        self.device = torch.device('cuda:' + str(config['gpu']) if self.with_cuda else 'cpu')
        self.model = self.model.to(self.device)

        # Logging and writers:
        self.train_logger = train_logger
        self.writer = WriterTensorboardX(config)

        # Optimizer and learning rate scheduler:
        self.optimizer, self.lr_scheduler = get_optimizer(model, config['optimizer'])
        if self.lr_scheduler:
            self.lr_scheduler_freq = config['optimizer']['lr_scheduler']['step_freq']

        # Training parameter to monitor, and whether max or min is target:
        self.monitor = config['trainer']['monitor']
        self.monitor_mode = config['trainer']['monitor_mode']
        assert self.monitor_mode in ['min', 'max'], "Invalid value for 'monitor_mode'"

        self.monitor_best = math.inf if self.monitor_mode == 'min' else -math.inf
        self.start_epoch = 1

        # Save configuration into checkpoint directory:
        start_time = datetime.datetime.now().strftime('%m%d_%H%M')
        self.checkpoint_dir = os.path.join(config['trainer']['save_dir'], config['name'], start_time)
        ensure_dir(self.checkpoint_dir)
        config_save_path = os.path.join(self.checkpoint_dir, 'config.json')
        with open(config_save_path, 'w') as handle:
            json.dump(config, handle, indent=4, sort_keys=False)

        if resume:
            self._resume_checkpoint(resume)

    def train(self):
        """
        Full training logic
        """
        for epoch in range(self.start_epoch, self.epochs + 1):
            # Train one epoch:
            log = self._train_epoch(epoch)

            # Add epoch to logger:
            if self.train_logger:
                self.train_logger.add_entry(log)
                if self.verbosity >= 1:
                    for key, value in log.items():
                        self.logger.info('    {:15s}: {}'.format(str(key), value))

            # If current epoch model is 'new best', override/store it as best epoch:
            if self._new_best_model(log):
                self.monitor_best = log[self.monitor]
                self._save_checkpoint(epoch, log, save_best=True)

            # Save model of current epoch (in alignment with config['trainer']['save_freq']):
            if epoch % self.save_freq == 0:
                self._save_checkpoint(epoch, log)

            # Check if learning rate should be updated:
            if self.lr_scheduler and epoch % self.lr_scheduler_freq == 0:
                self.lr_scheduler.step(epoch)
                lr = self.lr_scheduler.get_lr()[0]
                self.logger.info('New Learning Rate: {:.6f}'.format(lr))

    def _new_best_model(self, log):
        """Returns 'True' if current epoch is best until this point in training, 'False' otherwise."""
        criteria_a =  (self.monitor_mode == 'min' and log[self.monitor] < self.monitor_best)
        criteria_b =  (self.monitor_mode == 'max' and log[self.monitor] > self.monitor_best)

        new_best_check = criteria_a or criteria_b

        return new_best_check

    def _train_epoch(self, epoch):
        """
        Training logic for an epoch

        :param epoch: Current epoch number
        """
        raise NotImplementedError

    def _save_checkpoint(self, epoch, log, save_best=False):
        """
        Saving checkpoints

        :param epoch: current epoch number
        :param log: logging information of the epoch
        :param save_best: if True, rename the saved checkpoint to 'model_best.pth.tar'
        """
        arch = type(self.model).__name__
        state = {
            'arch': arch,
            'epoch': epoch,
            'logger': self.train_logger,
            'state_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'monitor_best': self.monitor_best,
            'config': self.config
        }
        filename = os.path.join(self.checkpoint_dir, 'checkpoint-epoch{:03d}-loss-{:.4f}.pth.tar'
                                .format(epoch, log['loss']))
        torch.save(state, filename)
        if save_best:
            os.replace(filename, os.path.join(self.checkpoint_dir, 'model_best.pth.tar'))
            self.logger.info("Saving current best: {} ...".format('model_best.pth.tar'))
        else:
            self.logger.info("Saving checkpoint: {} ...".format(filename))

    def _resume_checkpoint(self, resume_path):
        """
        Resume from saved checkpoints

        :param resume_path: Checkpoint path to be resumed
        """
        self.logger.info("Loading checkpoint: {} ...".format(resume_path))
        checkpoint = torch.load(resume_path)
        self.start_epoch = checkpoint['epoch'] + 1
        self.monitor_best = checkpoint['monitor_best']
        self.model.load_state_dict(checkpoint['state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        if self.with_cuda:
            for state in self.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cuda(self.device)
        self.train_logger = checkpoint['logger']
        self.config = checkpoint['config']
        self.logger.info("Checkpoint '{}' (epoch {}) loaded".format(resume_path, self.start_epoch))
