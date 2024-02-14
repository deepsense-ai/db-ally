# mypy: disable-error-code="empty-body"
from unittest.mock import AsyncMock, Mock

import pytest
import sqlalchemy

import dbally
from dbally import SqlAlchemyBaseView
from dbally.audit.event_store import EventStore
from dbally.view_selection.llm_view_selector import LLMViewSelector


class MockView1(SqlAlchemyBaseView):
    """Mock View 1 Description"""

    def get_select(self) -> sqlalchemy.Select:
        ...


class MockView2(SqlAlchemyBaseView):
    """Mock View 2 Description"""

    def get_select(self) -> sqlalchemy.Select:
        ...


@pytest.fixture
def llm_client():
    llm_client = Mock()
    llm_client.text_generation = AsyncMock(return_value="MockView1")
    return llm_client


@pytest.fixture
def event_store():
    return EventStore()


@pytest.fixture
def views():
    dbally.use_openai_llm(openai_api_key="sk-fake")
    mock_collection = dbally.create_collection("mock_collection")
    mock_collection.add(MockView1)
    mock_collection.add(MockView2)
    return mock_collection.list()


@pytest.mark.asyncio
async def test_view_selection(llm_client, event_store, views):
    view_selector = LLMViewSelector(llm_client)

    view = await view_selector.select_view("Mock question?", views, event_store)
    assert view == "MockView1"
