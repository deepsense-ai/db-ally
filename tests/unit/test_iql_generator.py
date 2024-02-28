# mypy: disable-error-code="empty-body"

from unittest.mock import AsyncMock, Mock

import pytest
import sqlalchemy

from dbally import decorators
from dbally.audit.event_tracker import EventTracker
from dbally.data_models.prompts.iql_prompt_template import default_iql_template
from dbally.iql import IQLActions, IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.views.methods_base import MethodsBaseView


class MockView(MethodsBaseView):
    def get_select(self) -> sqlalchemy.Select:
        ...

    def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def apply_actions(self, actions: IQLActions) -> None:
        ...

    def execute(self, dry_run: bool = False):
        ...

    @decorators.view_filter()
    def filter_by_id(self, idx: int) -> sqlalchemy.ColumnElement:
        ...

    @decorators.view_filter()
    def filter_by_name(self, city: str) -> sqlalchemy.ColumnElement:
        ...

    @decorators.view_action()
    def sort_by_id(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        ...

    @decorators.view_action()
    def group_by_name(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        ...


@pytest.fixture
def view():
    view = MockView()
    return view


@pytest.fixture
def llm_client():
    mock_client = Mock()
    mock_client.text_generation = AsyncMock(return_value='{"filters": "LLM IQL mock answer"}')
    return mock_client


@pytest.fixture
def event_tracker():
    return EventTracker()


@pytest.mark.asyncio
async def test_iql_generation(llm_client, event_tracker, view):
    iql_generator = IQLGenerator(llm_client, default_iql_template)

    filters_for_prompt, actions_for_prompt = iql_generator._promptify_view(view.list_filters(), view.list_actions())
    filters_in_prompt = set(filters_for_prompt.split("\n"))
    actions_in_prompt = set(actions_for_prompt.split("\n"))

    assert filters_in_prompt == {"filter_by_id(idx: int)", "filter_by_name(city: str)"}
    assert actions_in_prompt == {"sort_by_id()", "group_by_name()"}

    response = await iql_generator.generate_iql(
        view.list_filters(), view.list_actions(), "Mock_question", event_tracker
    )
    assert response == ("LLM IQL mock answer", "")
