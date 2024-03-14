from typing import TYPE_CHECKING, List

from . import syntax
from ._processor import IQLProcessor

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
        return cls(await IQLProcessor(source, allowed_functions).process())
