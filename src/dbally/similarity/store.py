import abc
from typing import List, Optional


class SimilarityStore(metaclass=abc.ABCMeta):
    """
    Base class for all stores. Has to be able to store the data and retrieve it.

    This component is used while mapping a user input to the closest matching value in the data source.

    In particular, it is used inside `SimilarityIndex`, allowing the system to
    find the closest match to the user's input.
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
            The most similar text or None if no similar text is found.
        """
