from contextlib import contextmanager
from typing import Type, List

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_span import EventSpan


class EventStore:
    _handlers: List[EventHandler]

    def __init__(self):
        self._handlers = []

    @classmethod
    def initialize_with_handlers(cls, event_handlers: List[Type[EventHandler]]):
        instance = cls()

        for handler in event_handlers:
            handler_instance = handler()
            instance.subscribe(handler_instance)

        return instance

    def request_start(self, event: dict):
        for handler in self._handlers:
            handler.request_start(event)

    def request_end(self, event: dict):
        for handler in self._handlers:
            handler.request_end(event)

    def subscribe(self, event_handler: EventHandler):
        self._handlers.append(event_handler)

    @contextmanager
    def process_event(self, event: dict):
        handler_outputs = {}

        for handler in self._handlers:
            output = handler.event_start(event)
            handler_outputs[handler] = output

        span = EventSpan()
        yield span

        for handler in self._handlers:
            handler.event_end(span._data, handler_outputs[handler])
