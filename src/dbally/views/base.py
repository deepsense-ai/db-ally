import abc
from dataclasses import dataclass
from typing import Any, Dict, List

from dbally.iql import IQLActions, IQLQuery


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


@dataclass
class ExecutionResult:
    """
    Represents the result of the query execution.
    """

    results: List[Dict[str, Any]]
    context: Dict[str, Any]


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
    def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: IQLQuery object representing the filters to apply
        """

    @abc.abstractmethod
    def apply_actions(self, actions: IQLActions) -> None:
        """
        Applies the chosen actions to the view.

        :param actions: IQLActions object representing the actions to apply
        """

    # TODO: this should probably be replaced with a `dry_run` option on `execute`
    @abc.abstractmethod
    def generate_sql(self) -> str:
        """
        Generates SQL based on the applied filters and actions.
        """

    @abc.abstractmethod
    def execute(self) -> ExecutionResult:
        """
        Executes the query and returns the result.
        """
