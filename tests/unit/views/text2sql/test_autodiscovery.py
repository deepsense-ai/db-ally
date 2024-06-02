from unittest.mock import AsyncMock, Mock

import pytest
import sqlalchemy
from sqlalchemy import Engine, text

from dbally_codegen.autodiscovery import configure_text2sql_auto_discovery


@pytest.fixture
def sample_db() -> Engine:
    engine = sqlalchemy.create_engine("sqlite:///:memory:")

    statements = [
        "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)",
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL)",
        "CREATE TABLE authentication (id INTEGER PRIMARY KEY, username TEXT, password TEXT)",
    ]

    with engine.connect() as conn:
        for statement in statements:
            conn.execute(text(statement))

    return engine


def test_builder_cant_set_whitelist_and_blacklist():
    engine = Mock()

    builder = configure_text2sql_auto_discovery(engine)
    builder = builder.with_blacklist(["table1"])
    with pytest.raises(ValueError):
        builder.with_whitelist(["table1"])

    builder = configure_text2sql_auto_discovery(engine)
    builder = builder.with_whitelist(["table1"])
    with pytest.raises(ValueError):
        builder.with_blacklist(["table1"])


async def test_autodiscovery_blacklist(sample_db: Engine):
    tables = await configure_text2sql_auto_discovery(sample_db).with_blacklist(["authentication"]).discover()
    table_names = [table.name for table in tables]

    assert len(table_names) == 2
    assert "customers" in table_names
    assert "orders" in table_names
    assert "authentication" not in table_names


async def test_autodiscovery_whitelist(sample_db: Engine):
    tables = await configure_text2sql_auto_discovery(sample_db).with_whitelist(["customers", "orders"]).discover()
    table_names = [table.name for table in tables]

    assert len(table_names) == 2
    assert "customers" in table_names
    assert "orders" in table_names
    assert "authentication" not in table_names


async def test_autodiscovery_llm_descriptions(sample_db: Engine):
    mock_client = Mock()
    mock_client.generate_text = AsyncMock(return_value="LLM mock answer")

    tables = await (
        configure_text2sql_auto_discovery(sample_db)
        .with_blacklist(["authentication"])
        .use_llm(mock_client)
        .generate_description_by_llm()
        .discover()
    )
    table_descriptions = [table.description for table in tables]

    assert len(table_descriptions) == 2
    assert table_descriptions[0] == "LLM mock answer"
    assert table_descriptions[1] == "LLM mock answer"
