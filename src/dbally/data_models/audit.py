from dataclasses import dataclass
from enum import Enum
from dbally.data_models.prompts.prompt_template import ChatFormat
from typing import Optional


class EventType(Enum):
    LLM = "LLM"


@dataclass
class LLMEvent:
    prompt: ChatFormat
    type: str
    response: Optional[dict] = None
    

@dataclass
class RequestStart:
    question: str


@dataclass
class RequestEnd:
    sql: str
