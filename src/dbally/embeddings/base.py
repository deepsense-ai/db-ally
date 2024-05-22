from abc import ABC, abstractmethod
from typing import List


class EmbeddingClient(ABC):
    """
    Abstract client for creating text embeddings.
    """

    @abstractmethod
    async def get_embeddings(self, data: List[str]) -> List[List[float]]:
        """
        Creates embeddings for the given strings.

        Args:
            data: List of strings to get embeddings for.

        Returns:
            List of embeddings for the given strings.
        """
