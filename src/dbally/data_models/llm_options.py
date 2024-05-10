from dataclasses import asdict, dataclass
from typing import List, Optional, Union

from openai import NOT_GIVEN, NotGiven


@dataclass
class LLMOptions:
    """
    Dataclass that represents all available LLM call options for the OpenAI API. Each of them is
    described in the [OpenAI API documentation](https://platform.openai.com/docs/api-reference/chat/create.)
    """

    frequency_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN
    max_tokens: Union[Optional[int], NotGiven] = NOT_GIVEN
    n: Union[Optional[int], NotGiven] = NOT_GIVEN
    presence_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN
    seed: Union[Optional[int], NotGiven] = NOT_GIVEN
    stop: Union[Optional[Union[str, List[str]]], NotGiven] = NOT_GIVEN
    temperature: Union[Optional[float], NotGiven] = NOT_GIVEN
    top_p: Union[Optional[float], NotGiven] = NOT_GIVEN

    dict = asdict

    def __or__(self, other: "LLMOptions") -> "LLMOptions":
        """
        Merges two LLMOptions, prioritizing non-NOT_GIVEN values from the 'other' object.
        """
        self_dict = asdict(self)
        other_dict = asdict(other)

        updated_dict = {
            key: other_dict.get(key, self_dict[key])
            if not isinstance(other_dict.get(key), NotGiven)
            else self_dict[key]
            for key in self_dict
        }

        return self.__class__(**updated_dict)
