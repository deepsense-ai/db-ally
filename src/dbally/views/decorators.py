import typing

from dbally.views.registry import ViewRegistry, default_registry


def view_filter() -> typing.Callable:
    """
    Decorator for marking a method as a filter

    :return: Function that returns the decorated method
    """

    def wrapped(func: typing.Callable) -> typing.Callable:  # pylint: disable=missing-return-doc
        func._methodDecorator = view_filter  # type:ignore # pylint: disable=protected-access
        return func

    return wrapped


def view_action() -> typing.Callable:
    """
    Decorator for marking a method as an action

    :return: Function that returns the decorated method
    """

    def wrapped(func: typing.Callable) -> typing.Callable:  # pylint: disable=missing-return-doc
        func._methodDecorator = view_action  # type: ignore # pylint: disable=protected-access
        return func

    return wrapped


def view(name: typing.Optional[str] = None, registry: ViewRegistry = default_registry) -> typing.Callable:
    """
    Decorator for registering a view

    :param name: Name of the view. If not provided, the name of the class will be used
    :param registry: Registry to register the view in (defaults to the default registry)
    :return: Function that returns the decorated class
    """

    def wrapped(cls: type) -> type:  # pylint: disable=missing-return-doc
        registry.register(cls, name)
        return cls

    return wrapped
