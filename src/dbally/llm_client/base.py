# disable args docstring check as args are documented in OpenAI API docs
# pylint: disable=W9015,R0914

import abc
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Dict, Generic, Optional, Type, TypeVar, Union

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.audit import LLMEvent
from dbally.prompts import ChatFormat, PromptBuilder, PromptTemplate

LLMClientOptions = TypeVar("LLMClientOptions")


@dataclass
class LLMOptions(ABC):
    """
    Abstract dataclass that represents all available LLM call options.
    """

    dict = asdict


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
        options = options if options else self.default_options

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