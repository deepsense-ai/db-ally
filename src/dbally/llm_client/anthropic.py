from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Union

from anthropic import NOT_GIVEN as ANTHROPIC_NOT_GIVEN
from anthropic import APIConnectionError, APIResponseValidationError, APIStatusError
from anthropic import NotGiven as AnthropicNotGiven

from dbally.data_models.audit import LLMEvent
from dbally.llm_client.base import LLMClient, LLMOptions
from dbally.prompts.common_validation_utils import extract_system_prompt
from dbally.prompts.prompt_builder import ChatFormat

from .._exceptions import LLMConnectionError, LLMResponseError, LLMStatusError
from .._types import NOT_GIVEN, NotGiven


@dataclass
class AnthropicOptions(LLMOptions):
    """
    Dataclass that represents all available LLM call options for the Anthropic API. Each of them is
    described in the [Anthropic API documentation](https://docs.anthropic.com/en/api/messages).
    """

    _not_given: ClassVar[Optional[AnthropicNotGiven]] = ANTHROPIC_NOT_GIVEN

    max_tokens: Union[int, NotGiven] = NOT_GIVEN
    stop_sequences: Union[Optional[List[str]], NotGiven] = NOT_GIVEN
    temperature: Union[Optional[float], NotGiven] = NOT_GIVEN
    top_k: Union[Optional[int], NotGiven] = NOT_GIVEN
    top_p: Union[Optional[float], NotGiven] = NOT_GIVEN

    def dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the LLMOptions instance.
        If a value is None, it will be replaced with a provider-specific not-given sentinel,
        except for max_tokens, which is set to 4096 if not provided.

        Returns:
            A dictionary representation of the LLMOptions instance.
        """
        options = super().dict()

        # Anthropic API requires max_tokens to be set
        if isinstance(options["max_tokens"], AnthropicNotGiven) or options["max_tokens"] is None:
            options["max_tokens"] = 4096

        return options


class AnthropicClient(LLMClient[AnthropicOptions]):
    """
    `AnthropicClient` is a class designed to interact with Anthropic's language model (LLM) endpoints,
    particularly for the Claude models.

    Args:
        model_name: Name of the [Anthropic's model](https://docs.anthropic.com/claude/docs/models-overview) to be used,\
            default is "claude-3-opus-20240229".
        api_key: Anthropic's API key. If None ANTHROPIC_API_KEY environment variable will be used.
        default_options: Default options to be used in the LLM calls.
    """

    _options_cls = AnthropicOptions

    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        default_options: Optional[AnthropicOptions] = None,
    ) -> None:
        try:
            from anthropic import AsyncAnthropic  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install anthropic package to use Claude models") from exc

        super().__init__(model_name=model_name, default_options=default_options)
        self._client = AsyncAnthropic(api_key=api_key)

    async def call(
        self,
        prompt: Union[str, ChatFormat],
        response_format: Optional[Dict[str, str]],
        options: AnthropicOptions,
        event: LLMEvent,
    ) -> str:
        """
        Calls the Anthropic API endpoint.

        Args:
            prompt: Prompt as an Anthropic client style list.
            response_format: Optional argument used in the OpenAI API - used to force the json output.
            options: Additional settings used by the LLM.
            event: Container with the prompt, LLM response and call metrics.

        Returns:
            Response string from LLM.

        Raises:
            LLMConnectionError: If there was an error connecting to the LLM API.
            LLMStatusError: If the LLM API returned an error status.
            LLMResponseError: If the LLM API returned an invalid response.
        """
        prompt, system = extract_system_prompt(prompt)

        try:
            response = await self._client.messages.create(
                messages=prompt,
                model=self.model_name,
                system=system,
                **options.dict(),  # type: ignore
            )
        except APIConnectionError as exc:
            raise LLMConnectionError() from exc
        except APIStatusError as exc:
            raise LLMStatusError(exc.message, exc.status_code) from exc
        except APIResponseValidationError as exc:
            raise LLMResponseError() from exc

        event.completion_tokens = response.usage.output_tokens
        event.prompt_tokens = response.usage.input_tokens
        event.total_tokens = response.usage.output_tokens + response.usage.input_tokens

        return response.content[0].text  # type: ignore
