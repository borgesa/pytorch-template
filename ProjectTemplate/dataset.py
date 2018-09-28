# Standard library imports:
# Third party imports:
from torch.utils.data import Dataset


class CustomDataset(Dataset):
    """Template for implementing your own custom dataset.

    See the official PyTorch tutorial for an example:
    https://pytorch.org/tutorials/beginner/data_loading_tutorial.html
    """
    def __init__(self, root):
        self.root = root
        # Implement dataset initialization code (required).

    def __len__(self):
        # Implement function returning the lenght of dataset (required).
        return None
    def __getitem__(self, index):
        # Implement function returning data point with index 'index' (required).
        sample, target = None, None
        return sample, target
