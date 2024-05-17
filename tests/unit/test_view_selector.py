# mypy: disable-error-code="empty-body"
# pylint: disable=missing-return-doc
from typing import Dict
from unittest.mock import AsyncMock, Mock

import pytest

import dbally
from dbally.audit.event_tracker import EventTracker
from dbally.llms.clients.base import LLMClient
from dbally.view_selection.llm_view_selector import LLMViewSelector

from .mocks import MockLLMClient
from .test_collection import MockView1, MockView2


@pytest.fixture
def llm_client() -> LLMClient:
    """Return a mock LLM client."""
    client = Mock()
    client.text_generation = AsyncMock(return_value="MockView1")
    return client


@pytest.fixture
def views() -> Dict[str, str]:
    """Return a map of view names + view descriptions to be used in the test."""
    mock_collection = dbally.create_collection("mock_collection", llm_client=MockLLMClient())
    mock_collection.add(MockView1)
    mock_collection.add(MockView2)
    return mock_collection.list()


@pytest.mark.asyncio
async def test_view_selection(llm_client: LLMClient, views: Dict[str, str]):
    view_selector = LLMViewSelector(llm_client)

    view = await view_selector.select_view("Mock question?", views, event_tracker=EventTracker())
    assert view == "MockView1"
