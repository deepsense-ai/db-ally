from __future__ import annotations

import enum
from pathlib import Path
from typing import Iterator

from pydantic import BaseModel, RootModel

from dbally.io import load_data


class DifficultyLevel(str, enum.Enum):
    """Enum representing Text2SQL example difficulty level."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    CHALLENGING = "challenging"


class Text2SQLExample(BaseModel):
    """Class for storing a single instance of Text2SQL example."""

    db_id: str
    question: str
    evidence: str
    SQL: str
    difficulty: DifficultyLevel


class Text2SQLDataset(RootModel):
    """Class for storing Text2SQL examples."""

    root: list[Text2SQLExample]

    def __iter__(self) -> Iterator[Text2SQLExample]:
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key: int) -> Text2SQLExample:
        return self.root[key]

    @classmethod
    def from_json_file(cls, file_path: Path) -> Text2SQLDataset:
        """
        Constructor for loading the dataset from a json file.

        Args:
            file_path: File from which the dataset should be read.

        Returns:
            Dataset object initiated from the file.
        """

        data = load_data(file_path)
        return cls.model_validate_json(data)


class Text2SQLResult(BaseModel):
    """Class for storing a single instance of Text2SQL evaluation result."""

    db_id: str
    question: str
    ground_truth_sql: str
    predicted_sql: str
