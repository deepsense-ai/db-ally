from dataclasses import dataclass
from typing import List, Optional

from dbally.similarity import SimilarityIndex


@dataclass
class ColumnConfig:
    """
    Configuration of a column used in the Text2SQL view.
    """

    name: str
    data_type: str
    description: Optional[str] = None
    similarity_index: Optional[SimilarityIndex] = None


@dataclass
class TableConfig:
    """
    Configuration of a table used in the Text2SQL view.
    """

    name: str
    columns: List[ColumnConfig]
    description: Optional[str] = None

    def __post_init__(self) -> None:
        self._column_index = {column.name: column for column in self.columns}

    @property
    def ddl(self) -> str:
        """
        Returns the DDL for the table which can be provided to the LLM as a context.

        Returns:
            The DDL for the table.
        """
        return (
            f"CREATE TABLE {self.name} ("
            + ", ".join(f"{column.name} {column.data_type}" for column in self.columns)
            + ");"
        )

    def __getitem__(self, item: str) -> ColumnConfig:
        return self._column_index[item]
