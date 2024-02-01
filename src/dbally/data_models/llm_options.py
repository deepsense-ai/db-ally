from dataclasses import asdict, dataclass
from typing import List, Optional, Union


@dataclass
class LLMOptions:
    """
    Dataclass that represents all available LLM call options. Each of them is
    described in details here: https://platform.openai.com/docs/api-reference/chat/create.
    """

    frequency_penalty: Optional[float]
    max_tokens: Optional[int]
    n: Optional[int]
    presence_penalty: Optional[float]
    seed: Optional[int]
    stop: Optional[Union[str, List[str]]]
    temperature: Optional[float]
    top_p: Optional[float]

    dict = asdict
