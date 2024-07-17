from functools import cached_property
from typing import Optional

from transformers import AutoTokenizer

from dbally.llms.base import LLM
from dbally.llms.clients.local import LocalLLMClient, LocalLLMOptions
from dbally.prompt.template import PromptTemplate


class LocalLLM(LLM[LocalLLMOptions]):
    """
    Class for interaction with any LLM available in HuggingFace.
    """

    _options_cls = LocalLLMOptions

    def __init__(
        self,
        model_name: str,
        default_options: Optional[LocalLLMOptions] = None,
        *,
        adapter_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Constructs a new local LLM instance.

        Args:
            model_name: Name of the model to use. This should be a model from the CausalLM class.
            default_options: Default options for the LLM.
            adapter_name: The name of the LoRA adapter, if any, used to modify the model's weights.
            api_key: The API key for Hugging Face authentication.
        """

        super().__init__(model_name, default_options)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=api_key)
        self.api_key = api_key
        self.adapter_name = adapter_name

    @cached_property
    def client(self) -> LocalLLMClient:
        """
        Client for the LLM.

        Returns:
            The client used to interact with the LLM.
        """
        return LocalLLMClient(model_name=self.model_name, adapter_name=self.adapter_name, hf_api_key=self.api_key)

    def count_tokens(self, prompt: PromptTemplate) -> int:
        """
        Counts tokens in the messages.

        Args:
            prompt: Messages to count tokens for.

        Returns:
            Number of tokens in the messages.
        """

        input_ids = self.tokenizer.apply_chat_template(prompt.chat)
        return len(input_ids)
