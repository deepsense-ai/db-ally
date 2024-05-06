from dataclasses import dataclass
from typing import List


@dataclass
class DdlColumn:
    """Dataclass that stores the information about a column in a DDL"""

    name: str
    type: str
    description: str = ""
    example_values: List[str]
    is_primary_key: bool = False
    is_foreign_key: bool = False

    def __str__(self):
        return f"{self.name} {self.type}"


@dataclass
class DDL:
    """Dataclass that stores the information about a DDL"""

    table_name: str
    columns: List[DdlColumn]
    description: str = ""

    def __str__(self):
        return f"CREATE TABLE {self.table_name} (\n" + ",\n".join([str(col) for col in self.columns]) + "\n);"
