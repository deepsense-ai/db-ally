from typing import List, Optional
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import create_engine

import dbally
from dbally.audit import CLIEventHandler, EventTracker, OtelEventHandler
from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.collection import Collection, ViewExecutionResult
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms import LLM
from dbally.llms.clients import LLMOptions
from dbally.views.freeform.text2sql import BaseText2SQLView, ColumnConfig, TableConfig
from tests.unit.mocks import MockIQLGenerator, MockLLM, MockViewBase, MockViewSelector

engine = create_engine("sqlite://", echo=True)


class MyText2SqlView(BaseText2SQLView):
    """
    A Text2SQL view for the example.
    """

    def get_tables(self) -> List[TableConfig]:
        return [
            TableConfig(
                name="mock_table",
                columns=[
                    ColumnConfig("mock_field1", "SERIAL PRIMARY KEY"),
                    ColumnConfig("mock_field2", "VARCHAR(255)"),
                ],
            ),
        ]

    async def ask(
        self,
        query: str,
        llm: LLM,
        event_tracker: EventTracker,
        n_retries: int = 3,
        dry_run: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ViewExecutionResult:
        return ViewExecutionResult(
            results=[{"mock_result": "fallback_result"}], context={"mock_context": "fallback_context"}
        )


class MockView1(MockViewBase):
    """
    Mock view 1
    """

    def execute(self, dry_run=False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[{"foo": "bar"}], context={"baz": "qux"})

    def get_iql_generator(self, *_, **__) -> MockIQLGenerator:
        raise UnsupportedQueryError


class MockView2(MockViewBase):
    """
    Mock view 2
    """


@pytest.fixture(name="base_collection")
def mock_base_collection() -> Collection:
    """
    Returns a collection with two mock views
    """
    collection = dbally.create_collection(
        "foo",
        llm=MockLLM(),
        view_selector=MockViewSelector("MockView1"),
        nl_responder=AsyncMock(),
    )
    collection.add(MockView1)
    collection.add(MockView2)
    return collection


@pytest.fixture(name="fallback_collection")
def mock_fallback_collection() -> Collection:
    """
    Returns a collection with two mock views
    """
    collection = dbally.create_collection(
        "fallback_foo",
        llm=MockLLM(),
        view_selector=MockViewSelector("MyText2SqlView"),
        nl_responder=AsyncMock(),
    )
    collection.add(MyText2SqlView, lambda: MyText2SqlView(engine))
    return collection


async def test_no_fallback_collection(base_collection: Collection, fallback_collection: Collection):
    with pytest.raises(UnsupportedQueryError) as exc_info:
        result = await base_collection.ask("Mock fallback question")
        print(result)
        print(exc_info)


async def test_fallback_collection(base_collection: Collection, fallback_collection: Collection):
    base_collection.set_fallback(fallback_collection)
    result = await base_collection.ask("Mock fallback question")
    assert result.results == [{"mock_result": "fallback_result"}]
    assert result.context == {"mock_context": "fallback_context"}


def test_get_all_event_handlers_no_fallback():
    handler1 = CLIEventHandler()
    handler2 = BufferEventHandler()

    collection = Collection(
        name="test_collection",
        llm=MockLLM(),
        nl_responder=AsyncMock(),
        view_selector=Mock(),
        event_handlers=[handler1, handler2],
    )

    result = collection.get_all_event_handlers()

    assert result == [handler1, handler2]


def test_get_all_event_handlers_with_fallback():
    handler1 = CLIEventHandler()
    handler2 = BufferEventHandler()
    handler3 = OtelEventHandler()

    fallback_collection = Collection(
        name="fallback_collection", view_selector=Mock(), llm=Mock(), nl_responder=Mock(), event_handlers=[handler3]
    )

    collection = Collection(
        name="test_collection",
        view_selector=Mock(),
        llm=MockLLM(),
        nl_responder=AsyncMock(),
        event_handlers=[handler1, handler2],
        fallback_collection=fallback_collection,
    )

    result = collection.get_all_event_handlers()

    assert set(result) == {handler1, handler2, handler3}


def test_get_all_event_handlers_with_duplicates():
    handler1 = CLIEventHandler()
    handler2 = BufferEventHandler()

    fallback_collection = Collection(
        name="fallback_collection", view_selector=Mock(), llm=Mock(), nl_responder=Mock(), event_handlers=[handler2]
    )

    collection = Collection(
        name="test_collection",
        view_selector=Mock(),
        llm=Mock(),
        nl_responder=Mock(),
        event_handlers=[handler1, handler2],
        fallback_collection=fallback_collection,
    )

    result = collection.get_all_event_handlers()

    assert set(result) == {handler1, handler2}
