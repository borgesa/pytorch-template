from torchvision.datasets import MNIST


def MnistDataset(*args, **kwargs):
    """Function returning MNIST class (as it's already implemented)."""
    return MNIST(*args, **kwargs)