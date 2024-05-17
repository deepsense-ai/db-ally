from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import litellm
from openai import APIConnectionError, APIResponseValidationError, APIStatusError

from dbally.data_models.audit import LLMEvent
from dbally.llms.clients.base import LLMClient, LLMOptions
from dbally.prompts import ChatFormat

from ..._exceptions import LLMConnectionError, LLMResponseError, LLMStatusError
from ..._types import NOT_GIVEN, NotGiven


@dataclass
class LiteLLMOptions(LLMOptions):
    """
    Dataclass that represents all available LLM call options for the LiteLLM client.
    Each of them is described in the [LiteLLM documentation](https://docs.litellm.ai/docs/completion/input).
    """

    frequency_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN
    max_tokens: Union[Optional[int], NotGiven] = NOT_GIVEN
    n: Union[Optional[int], NotGiven] = NOT_GIVEN
    presence_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN
    seed: Union[Optional[int], NotGiven] = NOT_GIVEN
    stop: Union[Optional[Union[str, List[str]]], NotGiven] = NOT_GIVEN
    temperature: Union[Optional[float], NotGiven] = NOT_GIVEN
    top_p: Union[Optional[float], NotGiven] = NOT_GIVEN


class LiteLLMClient(LLMClient[LiteLLMOptions]):
    """
    Client for the LiteLLM that supports calls to 100+ LLMs APIs, including OpenAI, Anthropic, VertexAI,
    Hugging Face and others.
    """

    _options_cls = LiteLLMOptions

    async def call(
        self,
        prompt: ChatFormat,
        response_format: Optional[Dict[str, str]],
        options: LiteLLMOptions,
        event: LLMEvent,
    ) -> str:
        """
        Calls the appropriate LLM endpoint with the given prompt and options.

        Args:
            prompt: Prompt as an OpenAI client style list.
            response_format: Optional argument used in the OpenAI API - used to force the json output
            options: Additional settings used by the LLM.
            event: Container with the prompt, LLM response and call metrics.

        Returns:
            Response string from LLM.

        Raises:
            LLMConnectionError: If there is a connection error with the LLM API.
            LLMStatusError: If the LLM API returns an error status code.
            LLMResponseError: If the LLM API response is invalid.
        """
        try:
            response = await litellm.acompletion(
                messages=prompt,
                model=self.model_name,
                api_key=self.api_key,
                response_format=response_format,
                **options.dict(),  # type: ignore
            )
        except APIConnectionError as exc:
            raise LLMConnectionError() from exc
        except APIStatusError as exc:
            raise LLMStatusError(exc.message, exc.status_code) from exc
        except APIResponseValidationError as exc:
            raise LLMResponseError() from exc

        event.completion_tokens = response.usage.completion_tokens
        event.prompt_tokens = response.usage.prompt_tokens
        event.total_tokens = response.usage.total_tokens

        return response.choices[0].message.content  # type: ignore
