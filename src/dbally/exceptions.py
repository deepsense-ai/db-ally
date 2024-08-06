class DbAllyError(Exception):
    """
    Base class for all exceptions raised by db-ally.
    """


class UnsupportedAggregationError(DbAllyError):
    """
    Error raised when AggregationFormatter is unable to construct a query
    with given aggregation.
    """
