def __get_start(depth):
    """
    get indentation level needed based on recursion depth
    :return: string w/ indentation level applied
    """
    # we uses tabs (\t) because it keeps everything nicely inline
    return ("\t" * depth) + "[*] "


def format_data(data):
    """
    :param data: input data
    :return: pretty formatted dictionary w/ recursion
    """
    formatted_string = ""
    if len(data) > 0:
        # upon first addition we don't want an increased depth (extra indentation level)
        # so we keep depth 0 when passing into these methods.
        if isinstance(data, dict):
            formatted_string += __format_dict(data, depth=0)
        elif isinstance(data, list):
            formatted_string += __format_list(data, depth=0)
    return formatted_string


def __format_dict(data, depth=0):
    """
    :param data: input dictionary
    :type data: dict
    :param depth: recursion depth; not to be set manually
    :type depth: int
    :return: pretty formatted dictionary w/ recursion
    """
    formatted_string = ""
    if len(data) == 0:
        return formatted_string
    start = __get_start(depth)
    last_key = list(data.keys())[-1]

    for key, value in data.items():
        if isinstance(value, dict):
            value = __format_dict(value, depth + 1)
            formatted_string += f"{start}{key}:\n{value}"
        elif isinstance(value, list):
            value = __format_list(value, depth + 1)
            formatted_string += f"{start}{key}:\n{value}"
        else:
            formatted_string += f"{start}{key}:\t{value}"

        if key != last_key:
            formatted_string += "\n"
    return formatted_string


def __format_list(data, depth):
    """
    :param data: input list
    :type data: list
    :param depth: recursion depth; not to be set manually
    :type depth: int
    :return: pretty formatted list w/ recursion
    """
    formatted_string = ""
    if len(data) == 0:
        return formatted_string
    start = __get_start(depth)
    last_item = data[-1]
    if not all([isinstance(item, dict) for item in data]):
        # if everything in the list is not a dict: add an indentation level
        # list of dictionaries look awkward when they move over two indentation levels w/o this
        depth += 1
    for item in data:

        if isinstance(item, dict):
            value = __format_dict(item, depth)
            formatted_string += value
        elif isinstance(item, list):
            value = __format_list(item, depth)
            formatted_string += value
        else:
            formatted_string += f"{start}{item}"

        if item != last_item:
            formatted_string += "\n"
    return formatted_string
