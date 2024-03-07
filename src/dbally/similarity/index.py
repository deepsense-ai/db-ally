import abc
from typing import Type

from dbally.similarity.fetcher import AbstractFetcher
from dbally.similarity.store import AbstractStore


class AnnotatedSimilarityIndex:
    """Stores information about the similarity index attached to a type."""

    __similarity_index__: "SimilarityIndex"
    __annotated_type__: type


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

    def annotated(self, base_type: type) -> Type:
        """
        Returns a new annotated type with similarity index attached.

        Args:
            base_type: type to be annotated.

        Returns:
            new annotated type
        """
        return type(
            f"Annotated_{self.__class__.__name__}_{base_type.__name__}",
            (base_type, AnnotatedSimilarityIndex),
            {"__similarity_index__": self, "__annotated_type__": base_type},
        )


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
