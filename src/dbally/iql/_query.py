from typing import TYPE_CHECKING, List, Optional

from ..audit.event_tracker import EventTracker
from . import syntax
from ._processor import IQLProcessor

if TYPE_CHECKING:
    from dbally.views.structured import ExposedFunction


class IQLQuery:
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: syntax.Node

    def __init__(self, root: syntax.Node, source: str) -> None:
        self.root = root
        self._source = source

    def __str__(self) -> str:
        return self._source

    @classmethod
    async def parse(
        cls,
        source: str,
        allowed_functions: List["ExposedFunction"],
        event_tracker: Optional[EventTracker] = None,
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
        root = await IQLProcessor(source, allowed_functions, event_tracker=event_tracker).process()
        return cls(root=root, source=source)
