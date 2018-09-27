# Standard library imports:
from importlib import import_module


def get_model_instance(model_config):
    model_arch = model_config['type']
    model_params = model_config['kwargs']

    # Separate module and class names:
    mod_name, class_name = model_arch.rsplit('.', 1)

    # Get module specified in configuration file:
    try:
        mod = import_module(mod_name)
    except ImportError:
        raise ImportError(f"No module named {mod_name} found.")

    # Get class specified in configuration file:
    try:
        model = getattr(mod, class_name)
    except AttributeError:
        raise AttributeError(f"No function '{class_name}' found in module '{mod_name}'")

    model_instance = model(**model_params)

    return model_instance


