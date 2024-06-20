import abc
from abc import ABC
from typing import Generic, TypeVar, Union

from strenum import StrEnum

from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart, SimilarityEvent

RequestCtx = TypeVar("RequestCtx")
EventCtx = TypeVar("EventCtx")


class LogLevel(StrEnum):
    """
    An enumeration representing different logging levels.

    This enumeration inherits from `StrEnum`, making each log level a string value.
    The log levels indicate the severity or type of events that occur within an application,
    and they are commonly used to filter and categorize log messages.

    Attributes:
        INFO (str): Represents informational messages that highlight the progress of the application.
        WARNING (str): Represents potentially harmful situations that require attention.
        ERROR (str): Represents error events that might still allow the application to continue running.
        DEBUG (str): Represents detailed debugging messages useful during development and troubleshooting.
    """

    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    DEBUG = "Debug"


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
    async def event_start(self, event: Union[LLMEvent, SimilarityEvent], request_context: RequestCtx) -> EventCtx:
        """
        Function that is called during every event execution.


        Args:
            event: db-ally event to be logged with all the details.
            request_context: Optional context passed from request_start method

        Returns:
            Implementation-specific request context object, which is passed to the `event_end` callback
        """

    @abc.abstractmethod
    async def event_end(
        self, event: Union[None, LLMEvent, SimilarityEvent], request_context: RequestCtx, event_context: EventCtx
    ) -> None:
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

    @abc.abstractmethod
    async def log_message(self, message: str, log_level: LogLevel = LogLevel.INFO) -> None:
        """
        Displays the response from the LLM.

        Args:
            message: db-ally event to be logged with all the details.
            log_level: log level/importance
        """
