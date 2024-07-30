from abc import ABC, abstractmethod
from typing import Dict, Iterable

from datasets import Dataset, load_dataset


class DataLoader(ABC):
    """
    Data loader.
    """

    def __init__(self, config: Dict) -> None:
        self.config = config

    @abstractmethod
    async def load(self) -> Iterable:
        """
        Load the data.

        Returns:
            The loaded data.
        """


class HuggingFaceDataLoader(DataLoader):
    """
    Hugging Face data loader.
    """

    async def load(self) -> Dataset:
        """
        Load the data from Hugging Face.

        Returns:
            The loaded data.
        """
        return load_dataset(
            path=self.config.data.path,
            split=self.config.data.split,
        )


class IQLViewDataLoader(HuggingFaceDataLoader):
    """
    Data loader for IQL view evaluation.
    """

    async def load(self) -> Dataset:
        """
        Load the data from Hugging Face and filter out samples without views.

        Returns:
            The loaded data.
        """
        dataset = await super().load()
        return dataset.filter(
            lambda x: x["db_id"] in self.config.data.db_ids
            and x["difficulty"] in self.config.data.difficulties
            and x["view_name"] is not None
        )


class SQLViewDataLoader(HuggingFaceDataLoader):
    """
    Data loader for SQL view evaluation.
    """

    async def load(self) -> Dataset:
        """
        Load the data from Hugging Face.

        Returns:
            The loaded data.
        """
        dataset = await super().load()
        return dataset.filter(
            lambda x: x["db_id"] in self.config.data.db_ids and x["difficulty"] in self.config.data.difficulties
        )


class CollectionDataLoader(HuggingFaceDataLoader):
    """
    Data loader for collection evaluation.
    """

    async def load(self) -> Dataset:
        """
        Load the data from Hugging Face.

        Returns:
            The loaded data.
        """
        dataset = await super().load()
        return dataset.filter(
            lambda x: x["db_id"] in self.config.data.db_ids and x["difficulty"] in self.config.data.difficulties
        )
