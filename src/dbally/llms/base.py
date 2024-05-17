from abc import ABC, abstractmethod
from functools import cached_property
from typing import Dict, Generic, Optional, Type

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.audit import LLMEvent
from dbally.llms.clients.base import LLMClient, LLMClientOptions, LLMOptions
from dbally.prompts.common_validation_utils import ChatFormat
from dbally.prompts.prompt_template import PromptTemplate


class LLM(Generic[LLMClientOptions], ABC):
    """
    Abstract class for the Language Model (LLM) interaction.
    """

    _options_cls: Type[LLMClientOptions]

    def __init__(
        self,
        model_name: str,
        default_options: Optional[LLMOptions] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Construct a new LLM instance.

        Args:
            model_name: Name of the model to be used.
            default_options: Default options to be used.
            api_key: API key to be used.

        Raises:
            TypeError: If the subclass is missing the '_options_cls' attribute.
        """
        self.model_name = model_name
        self.default_options = default_options or self._options_cls()
        self.api_key = api_key

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "_options_cls"):
            raise TypeError(f"Class {cls.__name__} is missing the '_options_cls' attribute")

    @cached_property
    @abstractmethod
    def _client(self) -> LLMClient:
        """
        Client for the LLM.
        """

    def _build_prompt(self, template: PromptTemplate, fmt: Dict[str, str]) -> ChatFormat:
        """
        Build prompt for the given template and format.

        Args:
            template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.

        Returns:
            Prompt in the format of the client.
        """
        return [{**message, "content": message["content"].format(**fmt)} for message in template.chat]

    def count_tokens(self, messages: ChatFormat, fmt: Dict[str, str]) -> int:
        """
        Count tokens in the messages.

        Args:
            messages: Messages to count tokens for.
            fmt: Arguments to be used with prompt.

        Returns:
            Number of tokens in the messages.
        """
        return sum(len(message["content"].format(**fmt)) for message in messages)

    async def text_generation(
        self,
        template: PromptTemplate,
        fmt: Dict[str, str],
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
            options: Options to use for the LLM client.

        Returns:
            Text response from LLM.
        """
        options = (self.default_options | options) if options else self.default_options
        prompt = self._build_prompt(template, fmt)
        event = LLMEvent(prompt=prompt, type=type(template).__name__)
        event_tracker = event_tracker or EventTracker()

        async with event_tracker.track_event(event) as span:
            event.response = await self._client.call(
                prompt=prompt,
                response_format=template.response_format,
                options=options,
                event=event,
            )
            span(event)

        return event.response
