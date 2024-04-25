from unittest.mock import AsyncMock, Mock

import pytest
import sqlalchemy
from sqlalchemy import Engine, text

from dbally.views.freeform.text2sql import configure_text2sql_auto_discovery


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
    config = await configure_text2sql_auto_discovery(sample_db).with_blacklist(["authentication"]).discover()

    assert len(config.tables) == 2

    tables = config.tables

    assert "customers" in tables
    assert "orders" in tables
    assert "authentication" not in tables


async def test_autodiscovery_whitelist(sample_db: Engine):
    config = await configure_text2sql_auto_discovery(sample_db).with_whitelist(["customers", "orders"]).discover()

    assert len(config.tables) == 2

    tables = config.tables

    assert "customers" in tables
    assert "orders" in tables
    assert "authentication" not in tables


async def test_autodiscovery_llm_descriptions(sample_db: Engine):
    mock_client = Mock()
    mock_client.text_generation = AsyncMock(return_value="LLM mock answer")

    config = await (
        configure_text2sql_auto_discovery(sample_db)
        .with_blacklist(["authentication"])
        .use_llm(mock_client)
        .generate_description_by_llm()
        .discover()
    )

    assert len(config.tables) == 2

    tables = config.tables

    assert tables["customers"].description == "LLM mock answer"
    assert tables["orders"].description == "LLM mock answer"
