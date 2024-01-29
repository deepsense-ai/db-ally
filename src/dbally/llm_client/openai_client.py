# disable args docstring check as args are documented in huggingface InferenceClient and OpenAI
# pylint: disable=W9015,R0914

from typing import Dict, List, Optional

from openai import AsyncOpenAI

from dbally.constants import GenerationModelType
from dbally.llm_client.base import LLMClient


class OpenAIClient(LLMClient):
    """Interface for interacting with OpenAI models."""

    def __init__(self) -> None:
        self.model_type = GenerationModelType.GPT4
        self._client = AsyncOpenAI()

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
        response = await self._client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            stop=stop_sequences,
            top_p=top_p,
            max_tokens=max_new_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        return response.choices[0].message.content
