import abc
import textwrap
from typing import Callable, List

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
        Returns:
            Filters defined inside the View and decorated with `decorators.view_filter`.
        """
        return self._list_methods_by_decorator(decorators.view_filter)
