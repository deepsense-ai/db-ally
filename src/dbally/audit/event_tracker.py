from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.events import Event, RequestEnd, RequestStart
from dbally.audit.spans import EventSpan


class EventTracker:
    """
    Container for event handlers and is responsible for processing events."""

    _handlers: List[EventHandler]
    _request_contexts: Dict[EventHandler, Optional[dict]]

    def __init__(self) -> None:
        self._handlers = []
        self._request_contexts = {}

    @classmethod
    def initialize_with_handlers(cls, event_handlers: List[EventHandler]) -> "EventTracker":
        """
        Initialize the event store with a list of event handlers.

        Args:
            event_handlers: List of event handlers.

        Returns:
            The initialized event store.
        """

        instance = cls()

        for handler in event_handlers:
            instance.subscribe(handler)

        return instance

    async def request_start(self, request_start: RequestStart) -> None:
        """
        Notify all event handlers about request start.

        Args:
            request_start: The request start event.
        """

        for handler in self._handlers:
            self._request_contexts[handler] = await handler.request_start(request_start)

    async def request_end(self, request_end: RequestEnd) -> None:
        """
        Notify all event handlers about request end.

        Args:
            request_end: The request end event.
        """

        for handler in self._handlers:
            await handler.request_end(request_end, request_context=self._request_contexts[handler])

    def subscribe(self, event_handler: EventHandler) -> None:
        """
        Add event handler to the store.

        Args:
            event_handler: Event handler to be added.
        """

        self._handlers.append(event_handler)

    @asynccontextmanager
    async def track_event(self, event: Event) -> AsyncIterator[EventSpan]:
        """
        Context manager for processing an event.

        Args:
            event: The event to be processed.

        Yields:
            Event span.
        """

        contexts = {}

        for handler in self._handlers:
            contexts[handler] = await handler.event_start(event, request_context=self._request_contexts[handler])

        span = EventSpan()
        yield span

        for handler in self._handlers:
            await handler.event_end(
                span.data, event_context=contexts[handler], request_context=self._request_contexts[handler]
            )
