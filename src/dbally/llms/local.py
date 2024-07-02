from functools import cached_property
from typing import Dict, Optional

import torch

from dbally.llms.base import LLM
from dbally.llms.clients.local import LocalLLMClient, LocalLLMOptions
from dbally.prompts.common_validation_utils import ChatFormat
from dbally.prompts.prompt_template import PromptTemplate


class LocalLLM(LLM[LocalLLMOptions, torch.tensor]):
    """
    Class for interaction with any LLM available in HuggingFace.
    """

    _options_cls = LocalLLMOptions

    def __init__(
        self,
        model_name: str,
        default_options: Optional[LocalLLMOptions] = None,
        *,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Constructs a new local LLM instance.

        Args:
            model_name: Name of the model to use. This should be a model from the CausalLM class.
            default_options: Default options for the LLM.
            api_key: The API key for Hugging Face authentication.
        """

        hf_model_name = model_name.split("/", 1)[1]

        super().__init__(hf_model_name, default_options)
        self.api_key = api_key

    @cached_property
    def client(self) -> LocalLLMClient:
        """
        Client for the LLM.

        Returns:
            The client used to interact with the LLM.
        """
        return LocalLLMClient(model_name=self.model_name, hf_api_key=self.api_key)

    def format_prompt(self, template: PromptTemplate, fmt: Dict[str, str]) -> torch.tensor:
        """
        Applies formatting to the prompt template and tokenizes it.

        Args:
            template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.

        Returns:
            Tokenized prompt.
        """

        prompt = [{**message, "content": message["content"].format(**fmt)} for message in template.chat]

        return self.client.tokenizer.apply_chat_template(prompt, add_generation_prompt=True, return_tensors="pt").to(
            self.client.model.device
        )

    def count_tokens(self, messages: ChatFormat, fmt: Dict[str, str]) -> int:
        """
        Counts tokens in the messages.

        Args:
            messages: Messages to count tokens for.
            fmt: Arguments to be used with prompt.

        Returns:
            Number of tokens in the messages.
        """

        return self.format_prompt(messages, fmt).shape[1]
