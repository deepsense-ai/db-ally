# disable args docstring check as args are documented in OpenAI API docs
import abc
from typing import List


class EmbeddingClient(metaclass=abc.ABCMeta):
    """Abstract client for creating text embeddings."""

    @abc.abstractmethod
    async def get_embeddings(self, data: List[str]) -> List[List[float]]:
        """
        For a given list of strings returns a list of embeddings.

        Args:
            data: List of strings to get embeddings for.

        Returns:
            List of embeddings for the given strings.
        """
