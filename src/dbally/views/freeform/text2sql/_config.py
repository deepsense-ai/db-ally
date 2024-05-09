from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import yaml


class Text2SQLSimilarityType(str, Enum):
    """
    Enum for the types of similarity indexes supported by Text2SQL.
    """

    SEMANTIC = "SEMANTIC"
    TRIGRAM = "TRIGRAM"


@dataclass
class Text2SQLTableConfig:
    """
    Configuration of a table used in the Text2SQL view.
    """

    ddl: str
    description: Optional[str] = None
    similarity: Optional[Dict[str, Text2SQLSimilarityType]] = None


class Text2SQLConfig:
    """
    Configuration object for the Text2SQL freeform view.
    """

    def __init__(self, tables: Dict[str, Text2SQLTableConfig]):
        self.tables = tables

    @classmethod
    def from_file(cls, file_path: Path) -> "Text2SQLConfig":
        """
        Load the configuration object from a file.

        Args:
            file_path: Path to the file containing the configuration.

        Returns:
            Text2SQLConfig: The configuration object.
        """
        data = yaml.safe_load(file_path.read_text())
        tables = {table_name: Text2SQLTableConfig(**table) for table_name, table in data.items()}
        return cls(tables=tables)

    def to_file(self, file_path: Path) -> None:
        """
        Save the configuration object to a file.

        Args:
            file_path: Path to the file where the configuration should be saved.
        """
        data = {table_name: table.__dict__ for table_name, table in self.tables.items()}
        file_path.write_text(yaml.dump(data))

    def iterate_similarity_indexes(self) -> Iterable[Tuple[str, str, Text2SQLSimilarityType]]:
        """
        Iterate over the similarity indexes in the configuration.

        Yields:
            The table name, column name, and similarity type.
        """
        for table_name, table in self.tables.items():
            if table.similarity:
                for column_name, similarity_type in table.similarity.items():
                    yield table_name, column_name, similarity_type
