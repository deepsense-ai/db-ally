from functools import cached_property
from typing import Optional

from dbally.llms.base import LLM
from dbally.llms.clients.local_llm import LocalLLMClient, LocalLLMOptions


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
        api_key: Optional[str] = None,
    ) -> None:
        """
        Constructs a new local LLM instance.

        Args:
            model_name: Name of the model to use.
            default_options: Default options for the LLM.
            api_key: The API key for Hugging Face authentication.
        """

        super().__init__(model_name, default_options)
        self.api_key = api_key

    @cached_property
    def client(self) -> LocalLLMClient:
        """
        Client for the LLM.

        Returns:
            The client used to interact with the LLM.
        """
        return LocalLLMClient(model_name=self.model_name, hf_api_key=self.api_key)
