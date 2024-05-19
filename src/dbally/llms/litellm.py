from functools import cached_property
from typing import Dict, Optional

from litellm import token_counter

from dbally.llms.base import LLM
from dbally.llms.clients.litellm import LiteLLMClient, LiteLLMOptions
from dbally.prompts import ChatFormat


class LiteLLM(LLM[LiteLLMOptions]):
    """
    Class for interaction with any LLM supported by LiteLLM API.
    """

    _options_cls = LiteLLMOptions

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        default_options: Optional[LiteLLMOptions] = None,
        *,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        """
        Construct a new LiteLLM instance.

        Args:
            model_name: Name of the [LiteLLM supported model](https://docs.litellm.ai/docs/providers) to be used,
                default is "gpt-3.5-turbo".
            default_options: Default options to be used.
            base_url: Base URL of the LLM API.
            api_key: API key to be used. API key to be used. If not specified, an environment variable will be used,
                for more information, follow the instructions for your specific vendor in the\
                [LiteLLM documentation](https://docs.litellm.ai/docs/providers).
            api_version: API version to be used. If not specified, the default version will be used.
        """
        super().__init__(model_name, default_options)
        self.base_url = base_url
        self.api_key = api_key
        self.api_version = api_version

    @cached_property
    def _client(self) -> LiteLLMClient:
        """
        Client for the LLM.
        """
        return LiteLLMClient(
            model_name=self.model_name,
            base_url=self.base_url,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def count_tokens(self, messages: ChatFormat, fmt: Dict[str, str]) -> int:
        """
        Count tokens in the messages using a specified model.

        Args:
            messages: Messages to count tokens for.
            fmt: Arguments to be used with prompt.

        Returns:
            Number of tokens in the messages.
        """
        return sum(token_counter(model=self.model_name, text=message["content"].format(**fmt)) for message in messages)
