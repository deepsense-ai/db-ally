from __future__ import annotations

import enum
from pathlib import Path
from typing import Iterator

from dbally_benchmark.utils import load_data
from pydantic import BaseModel, RootModel


class DifficultyLevel(str, enum.Enum):
    """Enum representing BIRD example difficulty level."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    CHALLENGING = "challenging"


class BIRDExample(BaseModel):
    """Class for storing a single instance of example."""

    db_id: str
    question: str
    evidence: str
    SQL: str
    difficulty: DifficultyLevel


class BIRDDataset(RootModel):
    """Class for storing BIRD benchmark examples."""

    root: list[BIRDExample]

    def __iter__(self) -> Iterator[BIRDExample]:  # type: ignore
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key: int) -> BIRDExample:
        return self.root[key]

    @classmethod
    def from_json_file(cls, file_path: Path, difficulty_levels: list[str] | None = None) -> BIRDDataset:
        """
        Constructor for loading the dataset from a json file.

        Args:
            file_path: File from which the dataset should be read.
            difficulty_levels: Difficulty levels by which the dataset will be filtered.

        Returns:
            Dataset object initiated from the file.
        """

        data = load_data(file_path)
        dataset_obj = cls.model_validate_json(data)

        if difficulty_levels:
            difficulty_levels = [DifficultyLevel(level) for level in difficulty_levels]
            dataset_obj.root = [item for item in dataset_obj.root if item.difficulty in difficulty_levels]

        return dataset_obj
