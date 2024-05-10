# disable args docstring check as args are documented in OpenAI API docs
# pylint: disable=W9015,R0914

import abc
from typing import Dict, Optional, Union

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.audit import LLMEvent
from dbally.data_models.llm_options import LLMOptions
from dbally.prompts.prompt_builder import ChatFormat, PromptBuilder, PromptTemplate


class LLMClient(abc.ABC):
    """
    Abstract client for interaction with LLM.

    It accepts parameters including the template, format, event tracker,
    and optional generation parameters like frequency_penalty, max_tokens, and temperature
    (the full list of options is provided by the [`LLMOptions` class][dbally.data_models.llm_options.LLMOptions]).
    It constructs a prompt using the `PromptBuilder` instance and generates text using the `self.call` method.
    """

    def __init__(self, model_name: str, default_options: Optional[LLMOptions] = None):
        self.model_name = model_name
        self._default_options = default_options or LLMOptions()
        self._prompt_builder = PromptBuilder(self.model_name)

    async def text_generation(  # pylint: disable=R0913
        self,
        template: PromptTemplate,
        fmt: dict,
        *,
        event_tracker: Optional[EventTracker] = None,
        options: Optional[LLMOptions] = None,
    ) -> str:
        """
        For a given a PromptType and format dict creates a prompt and
        returns the response from LLM.

        Args:
            template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.
            event_tracker: Event store used to audit the generation process.
            options: The options to use for the LLM client.

        Returns:
            Text response from LLM.
        """
        options = (self._default_options | options) if options else self._default_options

        prompt = self._prompt_builder.build(template, fmt)

        event = LLMEvent(prompt=prompt, type=type(template).__name__)

        event_tracker = event_tracker or EventTracker()
        async with event_tracker.track_event(event) as span:
            event.response = await self.call(prompt, template.response_format, options, event)
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
