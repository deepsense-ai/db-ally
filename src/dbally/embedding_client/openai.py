from typing import Any, Dict, List, Optional

from dbally.embedding_client.base import EmbeddingClient


class OpenAiEmbeddingClient(EmbeddingClient):
    """
    Client for creating text embeddings using OpenAI API.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small", openai_options: Optional[Dict] = None):
        """
        Initializes the OpenAiEmbeddingClient.

        Args:
            api_key: The OpenAI API key.
            model: The model to use for embeddings.
            openai_options: Additional options to pass to the OpenAI API.
        """
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.openai_options = openai_options

        try:
            from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("You need to install openai package to use GPT models") from exc

        self._openai = AsyncOpenAI(api_key=self.api_key)

    async def get_embeddings(self, data: List[str]) -> List[List[float]]:
        """
        For a given list of strings returns a list of embeddings.

        Args:
            data: List of strings to get embeddings for.

        Returns:
            List of embeddings for the given strings.
        """
        kwargs: Dict[str, Any] = {
            "model": self.model,
        }
        if self.openai_options:
            kwargs.update(self.openai_options)

        response = await self._openai.embeddings.create(
            input=data,
            **kwargs,
        )
        return [embedding.embedding for embedding in response.data]
