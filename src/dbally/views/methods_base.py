import abc
import inspect
import textwrap
from typing import Any, Callable, List, Tuple

from dbally.iql import syntax
from dbally.views import decorators
from dbally.views.base import AbstractBaseView, ExposedFunction, MethodParamWithTyping


class MethodsBaseView(AbstractBaseView, metaclass=abc.ABCMeta):
    """
    Base class for views that use view methods to expose filters.
    """

    # Method arguments that should be skipped when listing methods
    HIDDEN_ARGUMENTS = ["self", "select", "return"]

    def _list_methods_by_decorator(self, decorator: Callable) -> List[ExposedFunction]:
        """
        Lists all methods decorated with the given decorator.
        """
        methods = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if (
                hasattr(method, "_methodDecorator")
                and method._methodDecorator == decorator  # pylint: disable=protected-access
            ):
                annotations = method.__annotations__.items()
                methods.append(
                    ExposedFunction(
                        name=method_name,
                        description=textwrap.dedent(method.__doc__).strip() if method.__doc__ else "",
                        parameters=[
                            MethodParamWithTyping(n, t) for n, t in annotations if n not in self.HIDDEN_ARGUMENTS
                        ],
                    )
                )
        return methods

    def list_filters(self) -> List[ExposedFunction]:
        """
        Lists all available filters from the view based on the @filter decorator.

        :return: List of exposed filters
        """
        return self._list_methods_by_decorator(decorators.view_filter)

    def _method_with_args_from_call(
        self, func: syntax.FunctionCall, method_decorator: Callable
    ) -> Tuple[Callable, list]:
        """
        Converts a IQL FunctionCall node to a method object and its arguments.

        :param func: IQL FunctionCall node
        :param method_decorator: The decorator that thhe method should have

        :return: Tuple with the method object and its arguments
        """
        decorator_name = method_decorator.__name__

        if not hasattr(self, func.name):
            raise ValueError(f"The {decorator_name} method {func.name} doesn't exists")

        method = getattr(self, func.name)

        if (
            not hasattr(method, "_methodDecorator")
            or method._methodDecorator != method_decorator  # pylint: disable=protected-access
        ):
            raise ValueError(f"The method {func.name} is not decorated with {decorator_name}")

        return method, func.arguments

    async def call_filter_method(self, func: syntax.FunctionCall) -> Any:
        """
        Converts a IQL FunctonCall filter to a method call. If the method is a coroutine, it will be awaited.

        :param func: IQL FunctionCall node

        :return: The result of the method call
        """
        method, args = self._method_with_args_from_call(func, decorators.view_filter)

        if inspect.iscoroutinefunction(method):
            return await method(*args)
        return method(*args)
