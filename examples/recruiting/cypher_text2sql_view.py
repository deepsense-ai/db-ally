# pylint: disable=missing-return-doc, missing-function-docstring, missing-class-docstring, missing-return-type-doc
from typing import List

import sqlalchemy
from sqlalchemy import text

from dbally.views.freeform.text2sql import BaseText2SQLView, ColumnConfig, TableConfig


class SampleText2SQLViewCyphers(BaseText2SQLView):
    def get_tables(self) -> List[TableConfig]:
        return [
            TableConfig(
                name="security_specialists",
                columns=[
                    ColumnConfig("id", "SERIAL PRIMARY KEY"),
                    ColumnConfig("name", "VARCHAR(255)"),
                    ColumnConfig("cypher", "VARCHAR(255)"),
                ],
                description="Knowledge base",
            )
        ]


def create_freeform_memory_engine() -> sqlalchemy.Engine:
    freeform_engine = sqlalchemy.create_engine("sqlite:///:memory:")

    statements = [
        "CREATE TABLE security_specialists (id INTEGER PRIMARY KEY, name TEXT, cypher TEXT)",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Alice', 'HAMAC')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Bob', 'AES')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Charlie', 'RSA')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('David', 'SHA2')",
    ]

    with freeform_engine.connect() as conn:
        for statement in statements:
            conn.execute(text(statement))

        conn.commit()

    return freeform_engine
