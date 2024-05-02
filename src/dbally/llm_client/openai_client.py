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
        self._api_key = api_key

        self._client = self._create_client()
        super().__init__(model_name)

    def _create_client(self):
        try:
            from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install openai package to use GPT models") from exc

        return AsyncOpenAI(api_key=self._api_key)

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
        # if "turbo" not in self.model_name:
        #    response_format = None

        options_dict = {k: v for k, v in options.dict().items() if v is not None}

        response = await self._client.chat.completions.create(
            messages=prompt, model=self.model_name, **options_dict  # type: ignore
        )

        event.completion_tokens = response.usage.completion_tokens
        event.prompt_tokens = response.usage.prompt_tokens
        event.total_tokens = response.usage.total_tokens

        return response.choices[0].message.content  # type: ignore


class AzureOpenAIClient(OpenAIClient):

    """_summary_"""

    def __init__(self, azure_endpoint: str, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None) -> None:
        self._azure_endpoint = azure_endpoint

        super().__init__(model_name, api_key)

    def _create_client(self):
        """_summary_

        Raises:
            ImportError: _description_

        Returns:
            _type_: _description_
        """
        try:
            from openai import AsyncAzureOpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install openai package to use GPT models") from exc

        return AsyncAzureOpenAI(
            api_key=self._api_key, azure_endpoint=self._azure_endpoint, api_version="2024-02-01", timeout=60.0
        )
