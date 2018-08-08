def dList2Dict(l):
    """ Convert a double list ``[[key, value], [key, value]]`` into a
        dictionary
    """
    return {v[0]: v[1] for v in l}


def dict2dList(l):
    """ Convert a dictionary into a double list
    """
    return [[k, v] for k, v in l.items()]
