from typing import Dict, Optional, Union

from dbally.data_models.audit import LLMEvent
from dbally.data_models.llm_options import LLMOptions
from dbally.llm_client.base import LLMClient
from dbally.prompts.prompt_builder import ChatFormat


class OpenAIClient(LLMClient):
    """
    `OpenAIClient` is a class designed to interact with OpenAI's language model (LLM) endpoints,
    particularly for the GPT models.

    Args:
        model_name: Name of the [OpenAI's model](https://platform.openai.com/docs/models) to be used,
            default is "gpt-3.5-turbo".
        api_key: OpenAI's API key. If None OPENAI_API_KEY environment variable will be used
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None) -> None:
        try:
            from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install openai package to use GPT models") from exc

        super().__init__(model_name)
        self._client = AsyncOpenAI(api_key=api_key)

    async def call(
        self,
        prompt: Union[str, ChatFormat],
        response_format: Optional[Dict[str, str]],
        options: LLMOptions,
        event: LLMEvent,
    ) -> str:
        """
        Calls the OpenAI API endpoint.

        Args:
            prompt: Prompt as an OpenAI client style list.
            response_format: Optional argument used in the OpenAI API - used to force the json output
            options: Additional settings used by the LLM.
            event: container with the prompt, LLM response and call metrics.

        Returns:
            Response string from LLM.
        """

        # only "turbo" models support response_format argument
        # https://platform.openai.com/docs/api-reference/chat/create#chat-create-response_format
        if "turbo" not in self.model_name:
            response_format = None

        response = await self._client.chat.completions.create(
            messages=prompt, model=self.model_name, response_format=response_format, **options.dict()  # type: ignore
        )

        event.completion_tokens = response.usage.completion_tokens
        event.prompt_tokens = response.usage.prompt_tokens
        event.total_tokens = response.usage.total_tokens

        return response.choices[0].message.content  # type: ignore
