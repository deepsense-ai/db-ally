import textwrap
from typing import Dict, Optional, Type

from dbally.views.base import AbstractBaseView


class ViewRegistry:
    """
    Registry for views, used to register and retrieve views by name
    """

    def __init__(self) -> None:
        self._views: Dict[str, Type[AbstractBaseView]] = {}

    def register(self, view: Type[AbstractBaseView], name: Optional[str] = None) -> None:
        """
        Registers a view with a given name (or the name of the class if no name is provided)

        :param view: View class to register
        :param name: Name of the view (defaults to the name of the class)

        :raises ValueError: If a view with the given name is already registered
        """
        if name is None:
            name = view.__name__

        if name in self._views:
            raise ValueError(f"View with name {name} is already registered")

        self._views[name] = view

    def get(self, name: str) -> AbstractBaseView:
        """
        Returns an instance of the view with the given name

        :param name: Name of the view to return
        :return: View instance
        """
        return self._views[name]()

    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        :return: Dictionary of view names and descriptions
        """
        return {
            name: (textwrap.dedent(view.__doc__).strip() if view.__doc__ else "") for name, view in self._views.items()
        }


# Default registry
# One can create multiple registries if needed, but this one is used by default
default_registry = ViewRegistry()
