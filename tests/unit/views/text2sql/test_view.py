import json
from unittest.mock import AsyncMock

import pytest
import sqlalchemy
from sqlalchemy import Engine, text

import dbally
from dbally.views.freeform.text2sql import BaseText2SQLView, ColumnConfig, TableConfig
from tests.unit.mocks import MockLLM


class SampleText2SQLView(BaseText2SQLView):
    def get_tables(self):
        return [
            TableConfig(
                name="customers",
                columns=[
                    ColumnConfig("id", "SERIAL PRIMARY KEY"),
                    ColumnConfig("name", "VARCHAR(255)"),
                    ColumnConfig("city", "VARCHAR(255)"),
                    ColumnConfig("country", "VARCHAR(255)"),
                    ColumnConfig("age", "INTEGER"),
                ],
                description="Customers table",
            )
        ]


@pytest.fixture
def sample_db() -> Engine:
    engine = sqlalchemy.create_engine("sqlite:///:memory:")

    statements = [
        "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)",
        "INSERT INTO customers (name, city) VALUES ('Alice', 'New York')",
        "INSERT INTO customers (name, city) VALUES ('Bob', 'Los Angeles')",
        "INSERT INTO customers (name, city) VALUES ('Charlie', 'New York')",
        "INSERT INTO customers (name, city) VALUES ('David', 'Los Angeles')",
    ]

    with engine.connect() as conn:
        for statement in statements:
            conn.execute(text(statement))

        conn.commit()

    return engine


async def test_text2sql_view(sample_db: Engine):
    llm_response = {
        "sql": "SELECT * FROM customers WHERE city = :city",
        "parameters": [{"name": "city", "value": "New York"}],
    }
    llm = MockLLM()
    llm.client.call = AsyncMock(return_value=json.dumps(llm_response))

    collection = dbally.create_collection(name="test_collection", llm=llm)
    collection.add(SampleText2SQLView, lambda: SampleText2SQLView(sample_db))

    response = await collection.ask("Show me customers from New York")

    assert response.context["sql"] == llm_response["sql"]
    assert response.results == [
        {"id": 1, "name": "Alice", "city": "New York"},
        {"id": 3, "name": "Charlie", "city": "New York"},
    ]
