# mypy: disable-error-code="empty-body"

from unittest.mock import AsyncMock, Mock

import pytest
import sqlalchemy

from dbally import decorators
from dbally.audit.event_tracker import EventTracker
from dbally.data_models.prompts.iql_prompt_template import default_iql_template
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.views.methods_base import MethodsBaseView


class MockView(MethodsBaseView):
    def get_select(self) -> sqlalchemy.Select:
        ...

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run: bool = False):
        ...

    @decorators.view_filter()
    def filter_by_id(self, idx: int) -> sqlalchemy.ColumnElement:
        ...

    @decorators.view_filter()
    def filter_by_name(self, city: str) -> sqlalchemy.ColumnElement:
        ...


@pytest.fixture
def view():
    view = MockView()
    return view


@pytest.fixture
def llm_client():
    mock_client = Mock()
    mock_client.text_generation = AsyncMock(return_value="LLM IQL mock answer")
    return mock_client


@pytest.fixture
def event_tracker():
    return EventTracker()


@pytest.mark.asyncio
async def test_iql_generation(llm_client, event_tracker, view):
    iql_generator = IQLGenerator(llm_client, default_iql_template)

    filters_for_prompt = iql_generator._promptify_view(view.list_filters())
    filters_in_prompt = set(filters_for_prompt.split("\n"))

    assert filters_in_prompt == {"filter_by_id(idx: int)", "filter_by_name(city: str)"}

    response = await iql_generator.generate_iql(view.list_filters(), "Mock_question", event_tracker)

    template_after_response = default_iql_template.add_assistant_message(content="LLM IQL mock answer")
    assert response == ("LLM IQL mock answer", template_after_response)

    template_after_response = template_after_response.add_user_message(content="Mock_error")
    response2 = await iql_generator.generate_iql(
        view.list_filters(), "Mock_question", event_tracker, template_after_response
    )
    template_after_2nd_response = template_after_response.add_assistant_message(content="LLM IQL mock answer")
    assert response2 == ("LLM IQL mock answer", template_after_2nd_response)


def test_add_error_msg(llm_client):
    iql_generator = IQLGenerator(llm_client, default_iql_template)
    errors = [ValueError("Mock_error")]

    conversation = default_iql_template.add_assistant_message(content="Assistant")

    conversation_with_error = iql_generator.add_error_msg(conversation, errors)

    error_msg = iql_generator._ERROR_MSG_PREFIX + "Mock_error\n"
    assert conversation_with_error == conversation.add_user_message(content=error_msg)