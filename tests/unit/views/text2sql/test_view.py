from unittest.mock import AsyncMock

import pytest
import sqlalchemy
from sqlalchemy import Engine, text

import dbally
from dbally.views.freeform.text2sql import Text2SQLConfig, Text2SQLFreeformView
from dbally.views.freeform.text2sql._config import Text2SQLTableConfig
from tests.unit.mocks import MockLLM


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
    llm = MockLLM()
    llm._client.call = AsyncMock(return_value="SELECT * FROM customers WHERE city = 'New York'")

    config = Text2SQLConfig(
        tables={
            "customers": Text2SQLTableConfig(
                ddl="CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)",
                description="Customers table",
            )
        }
    )

    collection = dbally.create_collection(name="test_collection", llm=llm)
    collection.add(Text2SQLFreeformView, lambda: Text2SQLFreeformView(sample_db, config))

    response = await collection.ask("Show me customers from New York")

    assert response.context["sql"] == "SELECT * FROM customers WHERE city = 'New York'"
    assert response.results == [
        {"id": 1, "name": "Alice", "city": "New York"},
        {"id": 3, "name": "Charlie", "city": "New York"},
    ]
