# disable args docstring check as args are documented in huggingface InferenceClient and OpenAI
# pylint: disable=W9015,R0914

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from dbally.constants import GenerationModel


class LLMClient(ABC):
    """General interface for interacting with LLMs."""

    model_type: GenerationModel

    @abstractmethod
    async def text_generation(
        self,
        messages: List[Dict[str, str]],
        *,
        max_new_tokens: Optional[int] = 128,
        stop_sequences: Optional[List[str]] = None,
        temperature: Optional[float] = 0.0,
        top_p: Optional[float] = 1.0,
        frequency_penalty: Optional[float] = 0.5,
        presence_penalty: Optional[float] = 0.0
    ) -> str:
        """
        Given a prompt, generate the following text.

        Returns:
            text response from LLM
        """
