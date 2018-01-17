class ObjectNotFoundError(Exception):
    """ Object not found on chain
    """
    pass


class SportsNotFoundError(Exception):
    """ Sport not found
    """
    pass


class ObjectNotFoundInLookup(Exception):
    """ Object not found in the lookup
    """
    pass


class MissingMandatoryValue(Exception):
    """ Missing a mandatory value
    """
    pass
