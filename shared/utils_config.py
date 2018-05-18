import yaml


def load_config(config_file):
    """ Loads the config from a yaml file.

    Args:
        config_file (str): Name of the yaml file from which the config should
                           be loaded.

    Return:
        Configuration dictionary.
    """

    with open(config_file) as f:
        config = yaml.load(f)

    # check for "None" entries
    fix_none_entries(d=config)

    return config


def fix_none_entries(d):
    """Converts all "None" entries in the dictionary to NoneType.

    Args:
        d (dict): The dictionary to travers.
    """

    for k, v in d.items():
        if isinstance(v, dict):
            fix_none_entries(v)
        else:
            if v == "None":
                d[k] = None


def update_dict(d, d_to_update):
    """Updated one dictionary recursively with the entires of another.

    Args:
        d (dict): The dict used to update d_to_update.
        d_to_update (dict): The dictionary whose entries should be updated.
    """

    for k, v in d.items():
        if isinstance(v, dict):
            update_dict(v)
        else:
            d_to_update[k] = v
