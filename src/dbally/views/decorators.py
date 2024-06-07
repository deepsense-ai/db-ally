import typing
from typing import List, Protocol


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


class FewShotSelectorFunc(Protocol):
    """
    An interface defining the signature of function marked by `few_shot` decorator
    """

    def __call__(self, query: str) -> List:
        ...


def few_shot() -> FewShotSelectorFunc:
    """
    Decorator for marking a method as a few-shot selector

    Returns:
        Function that returns the decorated method
    """
    ignore_args = ["self", "return"]

    def wrapped(func: FewShotSelectorFunc) -> FewShotSelectorFunc:  # pylint: disable=missing-return-doc
        params = [(n, t) for n, t in func.__annotations__.items() if n not in ignore_args]
        if params and not issubclass(params[0][1], str):
            raise TypeError(
                "Function decorated with `few_shot` need to have first argument of `str` type. "
                "See `FewShotSelectorFunc` signature."
            )
        func._methodDecorator = few_shot  # type:ignore # pylint: disable=protected-access
        return func

    return wrapped
