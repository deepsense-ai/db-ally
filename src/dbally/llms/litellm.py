from functools import cached_property
from typing import Dict, Optional

from litellm import token_counter

from dbally.llms.base import LLM
from dbally.llms.clients.litellm import LiteLLMClient, LiteLLMOptions
from dbally.prompts import ChatFormat


class LiteLLM(LLM[LiteLLMOptions]):
    """
    LiteLLM supports 100+ LLMs, including GPT, Claude, Gemini and Hugging Face models.
    """

    _options_cls = LiteLLMOptions

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        default_options: Optional[LiteLLMOptions] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Construct a new LiteLLM instance.

        Args:
            model_name: Name of the model to be used.
            default_options: Default options to be used.
            api_key: API key to be used.
        """
        super().__init__(
            model_name=model_name,
            default_options=default_options,
            api_key=api_key,
        )

    @cached_property
    def _client(self) -> LiteLLMClient:
        """
        Client for the LLM.
        """
        return LiteLLMClient(self.model_name, self.api_key)

    def count_tokens(self, messages: ChatFormat, fmt: Dict[str, str]) -> int:
        """
        Count tokens in the messages.

        Args:
            messages: Messages to count tokens for.
            fmt: Arguments to be used with prompt.

        Returns:
            Number of tokens in the messages.
        """
        return sum(token_counter(model=self.model_name, text=message["content"].format(**fmt)) for message in messages)
