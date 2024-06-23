from __future__ import annotations

from pathlib import Path
from typing import Iterator

from pydantic import BaseModel, RootModel

from dbally.prompts.common_validation_utils import ChatFormat


class IQLExample(BaseModel):
    """
    Represents an individual IQL (Interactive Query Language) example.

    Attributes:
        prompt: The prompt associated with the IQL example, which can be of
        type ChatFormat or a string.
        iql: The IQL query string.
    """

    prompt: ChatFormat | str
    iql: str


class IQLDataset(RootModel):
    """
    Class for storing a collection of IQL examples.

    Attributes:
        root: A list of IQLExample objects.
    """

    root: list[IQLExample]

    def __iter__(self) -> Iterator[IQLExample]:
        return iter(self.root)

    def __getitem__(self, key: int) -> IQLExample:
        return self.root[key]

    @classmethod
    def from_json_file(cls, file_path: Path, encoding: str | None = None) -> IQLDataset:
        """
        Creates an IQLDataset instance from a JSON file.

        Args:
            file_path: The path to the JSON file containing the dataset.
            encoding: The encoding of the JSON file. Defaults to None,
            in which case the default system encoding is used.

        Returns:
            An IQLDataset object initialized from the data in the JSON file.
        """

        with open(file_path, encoding=encoding) as file_handle:
            data = file_handle.read()

        dataset_obj = cls.model_validate_json(data)

        return dataset_obj
