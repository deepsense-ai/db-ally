import abc
from typing import List, Optional


class AbstractStore(metaclass=abc.ABCMeta):
    """
    Base class for all stores. Has to be able to store the data and retrieve it.
    """

    @abc.abstractmethod
    async def store(self, data: List[str]) -> None:
        """
        Stores the data. Should replace the previously stored data.

        Args:
            data: The data to store.
        """

    @abc.abstractmethod
    async def find_similar(self, text: str) -> Optional[str]:
        """
        Finds the most similar text in the store or returns None if no similar text is found.

        Args:
            text: The text to find similar to.

        Returns:
            Optional[str]: The most similar text or None if no similar text is found.
        """
