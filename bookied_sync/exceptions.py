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


class CannotCreateWithParentInProposal(Exception):
    """ We cannot create new objects with parents sitting in other proposals
    """

    pass
