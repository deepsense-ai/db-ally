from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar

from dbally.data_models.audit import LLMEvent
from dbally.prompts import ChatFormat

from ..._types import NotGiven

LLMOptionsNotGiven = TypeVar("LLMOptionsNotGiven")
LLMClientOptions = TypeVar("LLMClientOptions", bound="LLMOptions")


@dataclass
class LLMOptions(ABC):
    """
    Abstract dataclass that represents all available LLM call options.
    """

    _not_given: ClassVar[Optional[LLMOptionsNotGiven]] = None

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

    def dict(self) -> Dict[str, Any]:
        """
        Creates a dictionary representation of the LLMOptions instance.
        If a value is None, it will be replaced with a provider-specific not-given sentinel.

        Returns:
            A dictionary representation of the LLMOptions instance.
        """
        options = asdict(self)
        return {
            key: self._not_given if value is None or isinstance(value, NotGiven) else value
            for key, value in options.items()
        }


class LLMClient(Generic[LLMClientOptions], ABC):
    """
    Abstract client for a direct communication with LLM.
    """

    def __init__(self, model_name: str) -> None:
        """
        Constructs a new LLMClient instance.

        Args:
            model_name: Name of the model to be used.
        """
        self.model_name = model_name

    @abstractmethod
    async def call(
        self,
        prompt: ChatFormat,
        response_format: Optional[Dict[str, str]],
        options: LLMClientOptions,
        event: LLMEvent,
    ) -> str:
        """
        Calls LLM inference API.

        Args:
            prompt: Prompt passed to the LLM.
            response_format: Optional argument used in the OpenAI API - used to force a json output
            options: Additional settings used by LLM.
            event: LLMEvent instance which fields should be filled during the method execution.

        Returns:
            Response string from LLM.
        """
