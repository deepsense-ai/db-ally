import abc
import ast
from dataclasses import dataclass
from typing import List


@dataclass
class MethodParamWithTyping:
    """
    Represents a method parameter with its type.
    """

    name: str
    type: type


@dataclass
class ExposedFunction:
    """
    Represents a function exposed to the AI model.
    """

    name: str
    description: str
    parameters: List[MethodParamWithTyping]


class AbstractBaseView(metaclass=abc.ABCMeta):
    """
    Base class for all views. Has to be able to list all available filters and actions, apply them and generate SQL,
    but ottherwise is implementation agnostic.
    """

    @abc.abstractmethod
    def list_filters(self) -> List[ExposedFunction]:
        """
        Lists all available filters.
        """

    @abc.abstractmethod
    def list_actions(self) -> List[ExposedFunction]:
        """
        Lists all available actions.
        """

    @abc.abstractmethod
    def apply_filters(self, filters: ast.expr) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: AST node representing the filters to apply
        """

    @abc.abstractmethod
    def apply_actions(self, actions: List[ast.Call]) -> None:
        """
        Applies the chosen actions to the view.

        :param actions: List of AST nodes representing the actions to apply
        """

    # TODO: this should probably be changed to method that executes the query and returns the result
    @abc.abstractmethod
    def generate_sql(self) -> str:
        """
        Generates SQL based on the applied filters and actions.
        """
