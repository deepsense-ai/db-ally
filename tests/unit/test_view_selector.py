# mypy: disable-error-code="empty-body"

from typing import Dict, Union

import pytest
import sqlalchemy

import dbally
from dbally import SqlAlchemyBaseView
from dbally.data_models.prompts.prompt_template import ChatFormat
from dbally.view_selection.default_view_selector import DefaultViewSelector


class MockLLMClient:
    def generate(self, prompt: Union[str, ChatFormat], response_format: Dict[str, str]) -> str:
        return "MockView1"


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
    return MockLLMClient()


@pytest.fixture
def views():
    mock_collection = dbally.create_collection("mock_collection")
    mock_collection.add(MockView1)
    mock_collection.add(MockView2)
    return mock_collection.list()


@pytest.mark.asyncio
async def test_view_selection(llm_client, views):
    view_selector = DefaultViewSelector(llm_client)

    view = await view_selector.select_view("Mock question?", views)
    assert view == "MockView1"
