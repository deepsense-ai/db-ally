from typing import TYPE_CHECKING, Iterator, List

from . import syntax
from ._parser import IQLParser

if TYPE_CHECKING:
    from dbally.views.base import ExposedFunction


class IQLQuery:
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: syntax.Node

    def __init__(self, root: syntax.Node):
        self.root = root

    @classmethod
    async def parse(cls, source: str, allowed_functions: List["ExposedFunction"]) -> "IQLQuery":
        """
        Parse IQL string to IQLQuery object.

        Args:
            source: IQL string that needs to be parsed
            allowed_functions: list of IQL functions that are allowed for this query

        Returns:
             IQLQuery object
        """
        return cls(await IQLParser(source, allowed_functions).parse())


class IQLActions:
    """
    IQLActions container. It stores list of function calls to apply in order.
    """

    actions: List[syntax.FunctionCall]

    def __init__(self, actions: List[syntax.FunctionCall]):
        self.actions = actions

    @classmethod
    async def parse(cls, source: str, allowed_functions: List["ExposedFunction"]) -> "IQLActions":
        """
        Parse IQL action string to IQLActions object.

        Args:
            source: IQL string that needs to be parsed
            allowed_functions: list of IQL functions that are allowed for this query

        Returns:
            IQLActions object
        """
        return cls(await IQLParser(source, allowed_functions).parse_actions())

    def __iter__(self) -> Iterator[syntax.FunctionCall]:
        yield from self.actions
