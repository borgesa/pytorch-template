# Standard library imports:
from importlib import import_module
# Local imports:
from data_utils.transforms import get_composed_transforms


def get_dataset(ds_config):
    """Returns dataset as specified in configuration.

    :param ds_config: 'dataset' section of configuration file
    :return: instance of dataset object
    """
    # Separate module and class names:
    mod_name, class_name = ds_config['type'].rsplit('.', 1)

    # Get module specified in configuration file:
    try:
        mod = import_module(mod_name)
    except ImportError:
        raise ImportError(f"No module named {mod_name} found.")

    # Get class specified in configuration file:
    try:
        dataset = getattr(mod, class_name)
    except AttributeError:
        raise AttributeError(f"No function '{class_name}' found in module '{mod_name}'")

    composed_transforms = get_composed_transforms(ds_config['transforms'])

    return dataset(transform=composed_transforms,
                   **ds_config['kwargs'])


