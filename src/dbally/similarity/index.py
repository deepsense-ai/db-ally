import abc

from dbally.similarity.fetcher import AbstractFetcher
from dbally.similarity.store import AbstractStore


class AbstractSimilarityIndex(metaclass=abc.ABCMeta):
    """
    Base class for all similarity indexes.

    Usually it is recommended to use the SimilarityIndex class directly instead. AbstractSimilarityIndex may be used
    to built custom index classes in more advanced cases when the clear separation of the store and the fetcher
    is not a useful abstraction.
    """

    @abc.abstractmethod
    async def update(self) -> None:
        """
        Updates the store with the latest data.
        """

    @abc.abstractmethod
    async def similar(self, text: str) -> str:
        """
        Finds the most similar text or returns the original text if no similar text is found.

        Args:
            text: The text to find similar to.

        Returns:
            str: The most similar text or the original text if no similar text is found.
        """


class SimilarityIndex(AbstractSimilarityIndex):
    """
    Merges the store and the fetcher to provide a simple interface for keeping
    the data store and the similairty store in sync and finding similar texts.
    """

    def __init__(self, store: AbstractStore, fetcher: AbstractFetcher):
        self.store = store
        self.fetcher = fetcher

    async def update(self) -> None:
        """
        Updates the store with the latest data from the fetcher.
        """
        data = await self.fetcher.fetch()
        await self.store.store(data)

    async def similar(self, text: str) -> str:
        """
        Finds the most similar text in the store or returns the original text if no similar text is found.

        Args:
            text: The text to find similar to.

        Returns:
            str: The most similar text or the original text if no similar text is found.
        """
        found = await self.store.find_similar(text)
        return found if found else text
