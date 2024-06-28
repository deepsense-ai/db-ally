from typing import TYPE_CHECKING, List, Optional

from ..audit.event_tracker import EventTracker
from . import syntax
from ._processor import IQLProcessor
from dbally.context.context import BaseCallerContext

if TYPE_CHECKING:
    from dbally.views.structured import ExposedFunction


class IQLQuery:
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: syntax.Node

    def __init__(self, root: syntax.Node):
        self.root = root

    @classmethod
    async def parse(
        cls,
        source: str,
        allowed_functions: List["ExposedFunction"],
        event_tracker: Optional[EventTracker] = None,
        context: Optional[List[BaseCallerContext]] = None
    ) -> "IQLQuery":
        """
        Parse IQL string to IQLQuery object.

        Args:
            source: IQL string that needs to be parsed
            allowed_functions: list of IQL functions that are allowed for this query
            event_tracker: EventTracker object to track events
        Returns:
             IQLQuery object
        """
        return cls(await IQLProcessor(source, allowed_functions, context, event_tracker).process())
