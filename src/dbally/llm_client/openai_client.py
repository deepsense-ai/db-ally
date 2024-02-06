from typing import Optional, Union

from dbally.data_models.llm_options import LLMOptions
from dbally.llm_client.base import LLMClient
from dbally.prompts.prompt_builder import ChatFormat


class OpenAIClient(LLMClient):
    """LLM Client for OpenAI endpoints."""

    def __init__(self, model_name: str, api_key: Optional[str] = None) -> None:
        try:
            from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install openai package to use GPT models") from exc

        super().__init__(model_name)
        self._client = AsyncOpenAI(api_key=api_key)

    async def _call(self, prompt: Union[str, ChatFormat], options: LLMOptions) -> str:
        """
        Calls OpenAI API endpoint.

        Args:
            prompt: Prompt as an OpenAI client style list.
            options: Additional settings used by LLM.

        Returns:
            Response string from LLM.
        """

        response = await self._client.chat.completions.create(
            messages=prompt, model=self._model_name, **options.dict()  # type: ignore
        )

        return response.choices[0].message.content  # type: ignore
