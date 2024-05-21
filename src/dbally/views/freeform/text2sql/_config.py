from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from dbally.similarity import SimilarityIndex


class ColumnConfig:
    """
    Configuration of a column used in the Text2SQL view.
    """

    def __init__(
        self,
        name: str,
        data_type: str,
        description: Optional[str] = None,
        similarity_index: Optional[SimilarityIndex] = None,
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.similarity_index = similarity_index


class TableConfig:
    """
    Configuration of a table used in the Text2SQL view.
    """

    def __init__(self, name: str, columns: List[ColumnConfig], description: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.description = description
        self._column_index = {column.name: column for column in columns}

    @property
    def ddl(self) -> str:
        """
        Returns the DDL for the table which can be provided to the LLM as a context.

        Returns:
            The DDL for the table.
        """
        return (
            f"CREATE TABLE {self.name} )"
            + ", ".join(f"{column.name} {column.data_type}" for column in self.columns)
            + ");"
        )

    def __getitem__(self, item: str) -> ColumnConfig:
        return self._column_index[item]


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
