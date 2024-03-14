import abc
import re
from dataclasses import dataclass
from typing import _GenericAlias  # type: ignore
from typing import List, Union

from dbally.data_models.execution_result import ExecutionResult
from dbally.iql import IQLQuery


def parse_param_type(param_type: Union[type, _GenericAlias]) -> str:
    """
    Parses the type of a method parameter and returns a string representation of it.

    Args:
        param_type: type of the parameter

    Returns:
        str: string representation of the type
    """
    if param_type in {int, float, str, bool, list, dict, set, tuple}:
        return param_type.__name__
    if param_type.__module__ == "typing":
        return re.sub(r"\btyping\.", "", str(param_type))

    return str(param_type)


@dataclass
class MethodParamWithTyping:
    """
    Represents a method parameter with its type.
    """

    name: str
    type: Union[type, _GenericAlias]

    def __str__(self) -> str:
        return f"{self.name}: {parse_param_type(self.type)}"


@dataclass
class ExposedFunction:
    """
    Represents a function exposed to the AI model.
    """

    name: str
    description: str
    parameters: List[MethodParamWithTyping]

    def __str__(self) -> str:
        base_str = f"{self.name}({', '.join(str(param) for param in self.parameters)})"

        if self.description != "":
            return f"{base_str} - {self.description}"

        return base_str


class AbstractBaseView(metaclass=abc.ABCMeta):
    """
    Base class for all views. Has to be able to list all available filters, apply them and generate SQL,
    but ottherwise is implementation agnostic.
    """

    @abc.abstractmethod
    def list_filters(self) -> List[ExposedFunction]:
        """
        Lists all available filters.
        """

    @abc.abstractmethod
    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: IQLQuery object representing the filters to apply
        """

    @abc.abstractmethod
    def execute(self, dry_run: bool = False) -> ExecutionResult:
        """
        Executes the query and returns the result.

        :param dry_run: if True, only generate the query without executing it
        """
