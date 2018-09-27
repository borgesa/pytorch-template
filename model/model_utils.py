import torch.optim as optim


def get_optimizer(model, config):
    """Get torch optimizer and learning rate scheduler with specified optimizer configuration."""

    # Getting the optimizer:
    optimizer_type = config['type']
    try:
        optimizer_ = getattr(optim, optimizer_type)
    except AttributeError:
        raise AttributeError(f"Optimizer '{optimizer_type}' not found.")

    # TODO: Consider another 'try':
    optimizer = optimizer_(model.parameters(), **config['kwargs'])

    # Get learning rate scheduler:
    try:
        lr_scheduler = getattr(optim.lr_scheduler,
                               config['lr_scheduler']['type'])
        # TODO: Evaluate using this instead (remove try)
        # lr_scheduler = getattr(optim.lr_scheduler,
        #                        config['lr_scheduler']['type'], None)
    except AttributeError:
        raise AttributeError(f"Learning rate '{config['lr_scheduler']['type']}' not found.")

    if lr_scheduler:
        lr_scheduler = lr_scheduler(optimizer,
                                    **config['lr_scheduler']['kwargs'])

    return optimizer, lr_scheduler
