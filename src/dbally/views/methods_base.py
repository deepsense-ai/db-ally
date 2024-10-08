import inspect
import textwrap
from abc import ABC
from typing import Any, Callable, List, Tuple

from dbally.iql import syntax
from dbally.views import decorators
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping
from dbally.views.structured import BaseStructuredView


class MethodsBaseView(BaseStructuredView, ABC):
    """
    Base class for views that use view methods to expose filters.
    """

    # Method arguments that should be skipped when listing methods
    HIDDEN_ARGUMENTS = ["cls", "self", "return"]

    @classmethod
    def list_methods_by_decorator(cls, decorator: Callable) -> List[ExposedFunction]:
        """
        Lists all methods decorated with the given decorator.

        Args:
            decorator: The decorator to filter the methods

        Returns:
            List of exposed methods
        """
        methods = []
        for method_name in dir(cls):
            method = getattr(cls, method_name)
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
                            MethodParamWithTyping(n, t) for n, t in annotations if n not in cls.HIDDEN_ARGUMENTS
                        ],
                    )
                )
        return methods

    def list_filters(self) -> List[ExposedFunction]:
        """
        List filters in the given view

        Returns:
            Filters defined inside the View and decorated with `decorators.view_filter`.
        """
        return self.list_methods_by_decorator(decorators.view_filter)

    def list_aggregations(self) -> List[ExposedFunction]:
        """
        List aggregations in the given view

        Returns:
            Aggregations defined inside the View and decorated with `decorators.view_aggregation`.
        """
        return self.list_methods_by_decorator(decorators.view_aggregation)

    def _method_with_args_from_call(
        self, func: syntax.FunctionCall, method_decorator: Callable
    ) -> Tuple[Callable, List]:
        """
        Converts a IQL FunctionCall node to a method object and its arguments.

        Args:
            func: IQL FunctionCall node
            method_decorator: The decorator that the method should have
                (currently allows discrimination between filters and aggregations)

        Returns:
            Tuple with the method object and its arguments
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

    async def _call_method(self, method: Callable, args: List) -> Any:
        """
        Calls the method with the given arguments. If the method is a coroutine, it will be awaited.

        Args:
            method: The method to call.
            args: The arguments to pass to the method.

        Returns:
            The result of the method call.
        """
        if inspect.iscoroutinefunction(method):
            return await method(*args)
        return method(*args)

    async def call_filter_method(self, func: syntax.FunctionCall) -> Any:
        """
        Converts a IQL FunctonCall filter to a method call. If the method is a coroutine, it will be awaited.

        Args:
            func: IQL FunctionCall node

        Returns:
            The result of the method call
        """
        method, args = self._method_with_args_from_call(func, decorators.view_filter)
        return await self._call_method(method, args)

    async def call_aggregation_method(self, func: syntax.FunctionCall) -> Any:
        """
        Converts a IQL FunctonCall aggregation to a method call. If the method is a coroutine, it will be awaited.

        Args:
            func: IQL FunctionCall node

        Returns:
            The result of the method call
        """
        method, args = self._method_with_args_from_call(func, decorators.view_aggregation)
        return await self._call_method(method, args)
