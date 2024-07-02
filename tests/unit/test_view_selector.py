# mypy: disable-error-code="empty-body"
# pylint: disable=missing-return-doc
from typing import Dict
from unittest.mock import AsyncMock

import pytest

import dbally
from dbally.audit.event_tracker import EventTracker
from dbally.llms.base import LLM
from dbally.view_selection.llm_view_selector import LLMViewSelector
from tests.unit.mocks import MockLLM
from tests.unit.test_collection import MockView1, MockView2


@pytest.fixture
def llm() -> LLM:
    """Return a mock LLM client."""
    llm = MockLLM()
    llm.client.call = AsyncMock(return_value="MockView1")
    return llm


@pytest.fixture
def views() -> Dict[str, str]:
    """Return a map of view names + view descriptions to be used in the test."""
    mock_collection = dbally.create_collection("mock_collection", llm=MockLLM())
    mock_collection.add(MockView1)
    mock_collection.add(MockView2)
    return mock_collection.list()


@pytest.mark.asyncio
async def test_view_selection(llm: LLM, views: Dict[str, str]) -> None:
    view_selector = LLMViewSelector(llm)
    view = await view_selector.select_view("Mock question?", views, event_tracker=EventTracker())
    assert view == "MockView1"
