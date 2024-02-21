import abc
from abc import ABC
from typing import Optional, Union

from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart


class EventHandler(ABC):
    """
    Base event handler interface.
    """

    @abc.abstractmethod
    async def request_start(self, user_request: RequestStart) -> Optional[dict]:
        """
        Log the start of the request.

        Args:
            user_request: The start of the request.
        """

    @abc.abstractmethod
    async def event_start(self, event: Union[LLMEvent], request_context: Optional[dict] = None) -> Optional[dict]:
        """
        Log the start of the event.

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method
        """

    @abc.abstractmethod
    async def event_end(
        self, event: Union[None, LLMEvent], request_context: Optional[dict] = None, event_context: Optional[dict] = None
    ) -> None:
        """
        Log the end of the event.

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method
            event_context: Optional context passed from event_start method
        """

    @abc.abstractmethod
    async def request_end(self, output: RequestEnd, request_context: Optional[dict] = None) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request.
            request_context: Optional context passed from request_start method
        """
