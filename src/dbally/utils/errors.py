class NoViewFoundError(Exception):
    """Error raised when there is no view with the given name"""


class UnsupportedQueryError(Exception):
    """
    Error raised when IQL generator is unable to construct a query
    with given filters.
    """
