from abc import ABC
from typing import TYPE_CHECKING, Generic, List, Optional, Type

from ..audit.event_tracker import EventTracker
from . import syntax
from ._processor import IQLAggregationProcessor, IQLFiltersProcessor, IQLProcessor, RootT

if TYPE_CHECKING:
    from dbally.views.structured import ExposedFunction


class IQLQuery(Generic[RootT], ABC):
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: RootT
    source: str
    _processor: Type[IQLProcessor[RootT]]

    def __init__(self, root: RootT, source: str) -> None:
        self.root = root
        self.source = source

    def __str__(self) -> str:
        return self.source

    @classmethod
    async def parse(
        cls,
        source: str,
        allowed_functions: List["ExposedFunction"],
        event_tracker: Optional[EventTracker] = None,
    ) -> "IQLQuery[RootT]":
        """
        Parse IQL string to IQLQuery object.

        Args:
            source: IQL string that needs to be parsed.
            allowed_functions: List of IQL functions that are allowed for this query.
            event_tracker: EventTracker object to track events.

        Returns:
            IQLQuery object.

        Raises:
            IQLError: If parsing fails.
        """
        root = await cls._processor(source, allowed_functions, event_tracker=event_tracker).process()
        return cls(root=root, source=source)


class IQLFiltersQuery(IQLQuery[syntax.Node]):
    """
    IQL filters query container.
    """

    _processor: Type[IQLFiltersProcessor] = IQLFiltersProcessor


class IQLAggregationQuery(IQLQuery[syntax.FunctionCall]):
    """
    IQL aggregation query container.
    """

    _processor: Type[IQLAggregationProcessor] = IQLAggregationProcessor
