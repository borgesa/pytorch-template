# Third party imports:
# import torch.nn as nn
# import torch.nn.functional as F
# Local imports:
from base import BaseModel


class CustomModel(BaseModel):
    """Template for implementing model.

    See official PyTorch tutorial for an example:
    https://pytorch.org/tutorials/beginner/pytorch_with_examples.html#pytorch-custom-nn-modules
    """
    def __init__(self, config):
        super().__init__()
        # Implementation of model here.

    def forward(self, x):
        # Implementation of forward function here.
        return None

