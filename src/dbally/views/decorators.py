import typing


def view_filter() -> typing.Callable:
    """
    Decorator for marking a method as a filter

    Returns:
        Function that returns the decorated method
    """

    def wrapped(func: typing.Callable) -> typing.Callable:  # pylint: disable=missing-return-doc
        func._methodDecorator = view_filter  # type:ignore # pylint: disable=protected-access
        return func

    return wrapped


def view_aggregation() -> typing.Callable:
    """
    Decorator for marking a method as an aggregation

    Returns:
        Function that returns the decorated method
    """

    def wrapped(func: typing.Callable) -> typing.Callable:  # pylint: disable=missing-return-doc
        func._methodDecorator = view_aggregation  # type:ignore # pylint: disable=protected-access
        return func

    return wrapped
