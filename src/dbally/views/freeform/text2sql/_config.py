from typing import List, Optional

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
            f"CREATE TABLE {self.name} ("
            + ", ".join(f"{column.name} {column.data_type}" for column in self.columns)
            + ");"
        )

    def __getitem__(self, item: str) -> ColumnConfig:
        return self._column_index[item]
