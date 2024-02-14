# disable args docstring check as args are documented in OpenAI API docs
# pylint: disable=W9015,R0914

import abc
from typing import List, Optional, Union

from dbally.audit.event_store import EventStore
from dbally.data_models.audit import LLMEvent
from dbally.data_models.llm_options import LLMOptions
from dbally.prompts.prompt_builder import ChatFormat, PromptBuilder, PromptTemplate


class LLMClient(abc.ABC):
    """Abstract client for interaction with LLM."""

    def __init__(self, model_name: str):
        self._model_name = model_name
        self._prompt_builder = PromptBuilder(self._model_name)

    async def text_generation(  # pylint: disable=R0913
        self,
        template: PromptTemplate,
        fmt: dict,
        event_store: EventStore,
        *,
        frequency_penalty: Optional[float] = 0.0,
        max_tokens: Optional[int] = 128,
        n: Optional[int] = 1,
        presence_penalty: Optional[float] = 0.0,
        seed: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        temperature: Optional[float] = 1.0,
        top_p: Optional[float] = 1.0,
    ) -> str:
        """
        For a given a PromptType and format dict creates a prompt and
        returns the response from LLM.

        Returns:
            Text response from LLM.
        """

        options = LLMOptions(
            frequency_penalty=frequency_penalty,
            max_tokens=max_tokens,
            n=n,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            top_p=top_p,
        )

        prompt = self._prompt_builder.build(template, fmt)

        event = LLMEvent(prompt=prompt, type=type(template).__name__)

        with event_store.process_event(event) as span:
            event.response = await self._call(prompt, options)
            span(event)

        return event.response

    @abc.abstractmethod
    async def _call(self, prompt: Union[str, ChatFormat], options: LLMOptions) -> str:
        """
        Calls LLM API endpoint.

        Args:
            prompt: Text to be asked.
            options: Additional settings used by LLM.

        Returns:
            Response string from LLM.
        """
