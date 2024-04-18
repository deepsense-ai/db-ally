import importlib
from types import ModuleType
from typing import Any, Dict, List, Optional, Type

from dbally.similarity import AbstractSimilarityIndex
from dbally.views import decorators
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping
from dbally.views.methods_base import MethodsBaseView


class SimilarityIndexDetectorException(Exception):
    """
    Exception that occured during similarity index discovery
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class SimilarityIndexDetector:
    """
    Class used to detect similarity indexes. Works with method-based views that inherit
    from MethodsBaseView (including all built-in dbally views). Automatically detects similarity
    indexes on arguments of view's filter methods.

    Args:
        module: The module to search for similarity indexes
        chosen_view_name: The name of the view to search in (optional, all views if None)
        chosen_method_name: The name of the method to search in (optional, all methods if None)
        chosen_argument_name: The name of the argument to search in (optional, all arguments if None)
    """

    def __init__(
        self,
        module: ModuleType,
        chosen_view_name: Optional[str] = None,
        chosen_method_name: Optional[str] = None,
        chosen_argument_name: Optional[str] = None,
    ):
        self.module = module
        self.chosen_view_name = chosen_view_name
        self.chosen_method_name = chosen_method_name
        self.chosen_argument_name = chosen_argument_name

    @classmethod
    def from_path(cls, path: str) -> "SimilarityIndexDetector":
        """
        Create a SimilarityIndexDetector object from a path string in the format
        "path.to.module:ViewName.method_name.argument_name" where each part after the
        colon is optional.

        Args:
            path: The path to the object

        Returns:
            The SimilarityIndexDetector object

        Raises:
            SimilarityIndexDetectorException: If the module is not found
        """
        module_path, *object_path = path.split(":")
        object_parts = object_path[0].split(".") if object_path else []
        chosen_view_name = object_parts[0] if object_parts else None
        chosen_method_name = object_parts[1] if len(object_parts) > 1 else None
        chosen_argument_name = object_parts[2] if len(object_parts) > 2 else None

        module = cls.get_module_from_path(module_path)
        return cls(module, chosen_view_name, chosen_method_name, chosen_argument_name)

    @staticmethod
    def get_module_from_path(module_path: str) -> ModuleType:
        """
        Get the module from the given path

        Args:
            module_path: The path to the module

        Returns:
            The module

        Raises:
            SimilarityIndexDetectorException: If the module is not found
        """
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as exc:
            raise SimilarityIndexDetectorException(f"Module {module_path} not found.") from exc
        return module

    def _is_methods_base_view(self, obj: Any) -> bool:
        """
        Check if the given object is a subclass of MethodsBaseView
        """
        return isinstance(obj, type) and issubclass(obj, MethodsBaseView) and obj is not MethodsBaseView

    def list_views(self) -> List[Type[MethodsBaseView]]:
        """
        List method-based views in the module, filtering by the chosen view name if given during initialization.

        Returns:
            List of views

        Raises:
            SimilarityIndexDetectorException: If the chosen view is not found
        """
        views = [
            getattr(self.module, name)
            for name in dir(self.module)
            if self._is_methods_base_view(getattr(self.module, name))
        ]
        if self.chosen_view_name:
            views = [view for view in views if view.__name__ == self.chosen_view_name]
            if not views:
                raise SimilarityIndexDetectorException(
                    f"View {self.chosen_view_name} not found in module {self.module.__name__}."
                )
        return views

    def list_filters(self, view: Type[MethodsBaseView]) -> List[ExposedFunction]:
        """
        List filters in the given view, filtering by the chosen method name if given during initialization.

        Args:
            view: The view

        Returns:
            List of filter names

        Raises:
            SimilarityIndexDetectorException: If the chosen method is not found
        """
        methods = view.list_methods_by_decorator(decorators.view_filter)
        if self.chosen_method_name:
            methods = [method for method in methods if method.name == self.chosen_method_name]
            if not methods:
                raise SimilarityIndexDetectorException(
                    f"Filter method {self.chosen_method_name} not found in view {view.__name__}."
                )
        return methods

    def list_arguments(self, method: ExposedFunction) -> List[MethodParamWithTyping]:
        """
        List arguments in the given method, filtering by the chosen argument name if given during initialization.

        Args:
            method: The method

        Returns:
            List of argument names

        Raises:
            SimilarityIndexDetectorException: If the chosen argument is not found
        """
        parameters = method.parameters
        if self.chosen_argument_name:
            parameters = [parameter for parameter in parameters if parameter.name == self.chosen_argument_name]
            if not parameters:
                raise SimilarityIndexDetectorException(
                    f"Argument {self.chosen_argument_name} not found in method {method.name}."
                )
        return parameters

    def list_indexes(self, view: Optional[Type[MethodsBaseView]] = None) -> Dict[AbstractSimilarityIndex, List[str]]:
        """
        List similarity indexes in the module, filtering by the chosen view, method and argument names if given
        during initialization.

        Args:
            view: The view to search in (optional, all views if None)

        Returns:
            Dictionary mapping indexes to method arguments that use them

        Raises:
            SimilarityIndexDetectorException: If any of the chosen path parts is not found
        """
        indexes: Dict[AbstractSimilarityIndex, List[str]] = {}
        views = self.list_views() if view is None else [view]
        for view_class in views:
            for method in self.list_filters(view_class):
                for parameter in self.list_arguments(method):
                    if parameter.similarity_index:
                        indexes.setdefault(parameter.similarity_index, []).append(
                            f"{view_class.__name__}.{method.name}.{parameter.name}"
                        )
        return indexes

    async def update_indexes(self) -> None:
        """
        Update similarity indexes in the module, filtering by the chosen view, method and argument names if given
        during initialization.

        Raises:
            SimilarityIndexDetectorException: If any of the chosen path parts is not found
        """
        indexes = self.list_indexes()
        if not indexes:
            raise SimilarityIndexDetectorException("No similarity indexes found.")
        for index in indexes:
            await index.update()
