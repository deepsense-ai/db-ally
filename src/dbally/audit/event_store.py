from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_span import EventSpan
from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart


class EventStore:
    """
    Container for event handlers and is responsible for processing events."""

    _handlers: list[EventHandler]

    def __init__(self) -> None:
        self._handlers = []

    @classmethod
    def initialize_with_handlers(cls, event_handlers: list[type[EventHandler]]) -> EventStore:
        """
        Initialize the event store with a list of event handlers.

        Args:
            event_handlers: List of event handlers.

        Returns:
            The initialized event store.
        """

        instance = cls()

        for handler in event_handlers:
            handler_instance = handler()
            instance.subscribe(handler_instance)

        return instance

    def request_start(self, request_start: RequestStart) -> None:
        """
        Notify all event handlers about request start.

        Args:
            request_start: The request start event.
        """

        for handler in self._handlers:
            handler.request_start(request_start)

    def request_end(self, request_end: RequestEnd) -> None:
        """
        Notify all event handlers about request end.

        Args:
            request_end: The request end event.
        """

        for handler in self._handlers:
            handler.request_end(request_end)

    def subscribe(self, event_handler: EventHandler) -> None:
        """
        Add event handler to the store.

        Args:
            event_handler: Event handler to be added.
        """

        self._handlers.append(event_handler)

    @contextmanager
    def process_event(self, event: LLMEvent) -> Iterator[EventSpan]:
        """
        Context manager for processing an event.

        Args:
            event: The event to be processed.

        Yields:
            Event span.
        """

        for handler in self._handlers:
            handler.event_start(event)

        span = EventSpan()
        yield span

        for handler in self._handlers:
            handler.event_end(span.data)
