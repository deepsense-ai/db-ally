from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dbally.data_models.prompts.prompt_template import ChatFormat


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

    prompt: ChatFormat
    type: str
    response: Optional[dict] = None


@dataclass
class RequestStart:
    """
    Class representing request start data.
    """

    question: str


@dataclass
class RequestEnd:
    """
    Class representing request end data.
    """

    sql: str
