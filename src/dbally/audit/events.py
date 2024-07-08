from abc import ABC
from dataclasses import dataclass
from typing import Optional, Union

from dbally.collection.results import ExecutionResult
from dbally.prompt.template import ChatFormat


@dataclass
class Event(ABC):
    """
    Base class for all events.
    """


@dataclass
class LLMEvent(Event):
    """
    Class for LLM event.
    """

    prompt: Union[str, ChatFormat]
    type: str
    response: Optional[str] = None

    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@dataclass
class SimilarityEvent(Event):
    """
    SimilarityEvent is fired when a SimilarityIndex lookup is performed.
    """

    store: str
    fetcher: str

    input_value: str
    output_value: Optional[str] = None


@dataclass
class FallbackEvent(Event):
    """
    FallbackEvent is fired when a processed view/collection raise an exception.
    """

    triggering_collection_name: str
    triggering_view_name: str
    fallback_collection_name: str
    error_description: str


@dataclass
class RequestStart:
    """
    Class representing request start data.
    """

    collection_name: str
    question: str


@dataclass
class RequestEnd:
    """
    Class representing request end data.
    """

    result: ExecutionResult
