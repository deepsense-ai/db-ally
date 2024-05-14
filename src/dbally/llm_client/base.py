# disable args docstring check as args are documented in OpenAI API docs
# pylint: disable=W9015,R0914

import abc
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Dict, Generic, Optional, Type, TypeVar, Union

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.audit import LLMEvent
from dbally.prompts import ChatFormat, PromptBuilder, PromptTemplate

from .._types import NotGiven

LLMOptionsNotGiven = TypeVar("LLMOptionsNotGiven")
LLMClientOptions = TypeVar("LLMClientOptions")


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
    Abstract client for interaction with LLM.

    It constructs a prompt using the `PromptBuilder` instance and generates text using the `self.call` method.
    """

    _options_cls: Type[LLMClientOptions]

    def __init__(self, model_name: str, default_options: Optional[LLMClientOptions] = None) -> None:
        self.model_name = model_name
        self.default_options = default_options or self._options_cls()
        self._prompt_builder = PromptBuilder(self.model_name)

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "_options_cls"):
            raise TypeError(f"Class {cls.__name__} is missing the '_options_cls' attribute")

    async def text_generation(  # pylint: disable=R0913
        self,
        template: PromptTemplate,
        fmt: dict,
        *,
        event_tracker: Optional[EventTracker] = None,
        options: Optional[LLMClientOptions] = None,
    ) -> str:
        """
        For a given a PromptType and format dict creates a prompt and
        returns the response from LLM.

        Args:
            template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.
            event_tracker: Event store used to audit the generation process.
            options: options to use for the LLM client.

        Returns:
            Text response from LLM.
        """
        options = (self.default_options | options) if options else self.default_options

        prompt = self._prompt_builder.build(template, fmt)

        event = LLMEvent(prompt=prompt, type=type(template).__name__)

        event_tracker = event_tracker or EventTracker()
        async with event_tracker.track_event(event) as span:
            event.response = await self.call(
                prompt=prompt,
                response_format=template.response_format,
                options=options,
                event=event,
            )
            span(event)

        return event.response

    @abc.abstractmethod
    async def call(
        self,
        prompt: Union[str, ChatFormat],
        response_format: Optional[Dict[str, str]],
        options: LLMOptions,
        event: LLMEvent,
    ) -> str:
        """
        Calls LLM API endpoint.

        Args:
            prompt: prompt passed to the LLM.
            response_format: Optional argument used in the OpenAI API - used to force a json output
            options: Additional settings used by LLM.
            event: an LLMEvent instance which fields should be filled during the method execution.

        Returns:
            Response string from LLM.
        """
