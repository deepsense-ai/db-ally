from contextlib import contextmanager

from dbally.audit.event_handlers.base import BaseEventHandler
from dbally.audit.event_span import EventSpan


class EventStore:

    def __init__(self):
        self._subscribers = []

    def subscribe(self, event_handler: BaseEventHandler):
        self._subscribers.append(event_handler)

    def send_event(self, event: dict):
        for subscriber in self._subscribers:
            subscriber.notify(event)

@contextmanager
def process_event(event: dict, event_store: EventStore):

    span = EventSpan()
    yield span
    event_store.send_event(span._data)
