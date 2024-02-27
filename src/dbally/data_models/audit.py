from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from dbally.data_models.prompts.prompt_template import ChatFormat
from dbally.views.base import ExecutionResult


class EventType(Enum):
    """
    Enum for event types.
    """

    LLM = "LLM"


@dataclass
class LLMEvent:
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
