import abc
from abc import ABC
from typing import Optional


class EventHandler(ABC):

    @abc.abstractmethod
    def request_start(self, user_input: dict):
        pass

    @abc.abstractmethod
    def event_start(self, event: dict) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def event_end(self, event: dict, start_event_payload: Optional[dict]) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def request_end(self, output: dict):
        pass
