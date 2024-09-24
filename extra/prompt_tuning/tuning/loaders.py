from abc import ABC, abstractmethod
from typing import Iterable, List

import dspy.datasets
from dspy import Example
from omegaconf import DictConfig


class DataLoader(ABC):
    """
    Data loader.
    """

    def __init__(self, config: DictConfig) -> None:
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

    async def load(self) -> List[Example]:
        """
        Load the data from Hugging Face.

        Returns:
            The loaded data.
        """
        dataloader = dspy.datasets.DataLoader()
        dataset = dataloader.from_huggingface(
            dataset_name=self.config.data.path, split=self.config.data.split, input_keys=("question",)
        )
        return [
            data
            for data in dataset
            if data["question"]
            if (
                data["db_id"] in self.config.data.db_ids
                if self.config.data.db_ids
                else True and data["difficulty"] in self.config.data.difficulties
                if self.config.data.difficulties
                else True
            )
        ]


class IQLGenerationDataLoader(HuggingFaceDataLoader):
    """
    Data loader for IQL generation evaluation.
    """

    async def load(self) -> List[Example]:
        """
        Load the data from Hugging Face and filter out samples without views.

        Returns:
            The loaded data.
        """
        dataset = await super().load()
        return [data for data in dataset if data["view_name"]]
