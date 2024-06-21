import abc
from abc import ABC
from typing import Generic, Optional, TypeVar

from dbally.audit.events import Event, RequestEnd, RequestStart

RequestCtx = TypeVar("RequestCtx")
EventCtx = TypeVar("EventCtx")


class EventHandler(Generic[RequestCtx, EventCtx], ABC):
    """
    A base class that every custom handler should inherit from
    """

    @abc.abstractmethod
    async def request_start(self, user_request: RequestStart) -> RequestCtx:
        """
        Function that is called at the beginning of every `Collection.ask` execution.

        Args:
            user_request: Object containing name of collection and asked query

        Returns:
            Implementation-specific request context object, which is passed to the future callbacks
        """

    @abc.abstractmethod
    async def event_start(self, event: Event, request_context: RequestCtx) -> EventCtx:
        """
        Function that is called during every event execution.


        Args:
            event: db-ally event to be logged with all the details.
            request_context: Optional context passed from request_start method

        Returns:
            Implementation-specific request context object, which is passed to the `event_end` callback
        """

    @abc.abstractmethod
    async def event_end(self, event: Optional[Event], request_context: RequestCtx, event_context: EventCtx) -> None:
        """
        Function that is called during every event execution.

        Args:
            event: db-ally event to be logged with all the details.
            request_context: Optional context passed from request_start method
            event_context: Optional context passed from event_start method
        """

    @abc.abstractmethod
    async def request_end(self, output: RequestEnd, request_context: RequestCtx) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request.
            request_context: Optional context passed from request_start method
        """
