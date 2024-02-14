import abc
from abc import ABC
from typing import Union

from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart


class EventHandler(ABC):
    """
    Base event handler interface.
    """

    @abc.abstractmethod
    def request_start(self, user_request: RequestStart) -> None:
        """
        Log the start of the request.

        Args:
            user_request: The start of the request.
        """

    @abc.abstractmethod
    def event_start(self, event: Union[LLMEvent]) -> None:
        """
        Log the start of the event.

        Args:
            event: Event to be logged.
        """

    @abc.abstractmethod
    def event_end(self, event: Union[LLMEvent]) -> None:
        """
        Log the end of the event.

        Args:
            event: Event to be logged.
        """

    @abc.abstractmethod
    def request_end(self, output: RequestEnd) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request.
        """
