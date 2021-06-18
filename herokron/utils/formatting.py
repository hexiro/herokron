import yaml


def format_data(data):
    """
    :param data: input data
    :return: pretty formatted yaml representation of a dictionary
    """
    return yaml.dump(data, sort_keys=False, default_flow_style=False)
