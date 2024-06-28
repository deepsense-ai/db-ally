# mypy: disable-error-code="empty-body"

from unittest.mock import AsyncMock

import pytest
import sqlalchemy

from dbally import decorators
from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.iql_prompt_template import IQL_GENERATION_TEMPLATE
from dbally.prompts.elements import FewShotExample
from dbally.prompts.formatters import IQLInputFormatter
from dbally.views.methods_base import MethodsBaseView
from tests.unit.mocks import MockLLM


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
def view() -> MockView:
    return MockView()


@pytest.fixture
def llm() -> MockLLM:
    llm = MockLLM()
    llm.client.call = AsyncMock(return_value="LLM IQL mock answer")
    return llm


@pytest.fixture
def event_tracker() -> EventTracker:
    return EventTracker()


@pytest.mark.asyncio
async def test_iql_generation(llm: MockLLM, event_tracker: EventTracker, view: MockView) -> None:
    iql_generator = IQLGenerator(llm)

    filters = {str(_filter) for _filter in view.list_filters()}
    assert filters == {"filter_by_id(idx: int)", "filter_by_name(city: str)"}

    input_formatter = IQLInputFormatter(question="Mock_question", filters=view.list_filters())
    template_after_response = input_formatter(IQL_GENERATION_TEMPLATE)

    response = await iql_generator.generate_iql(
        question="Mock_question",
        filters=view.list_filters(),
        event_tracker=event_tracker,
        prompt_template=IQL_GENERATION_TEMPLATE,
    )
    template_after_response = template_after_response.add_assistant_message(content="LLM IQL mock answer")
    assert response == ("LLM IQL mock answer", template_after_response)

    template_after_response = template_after_response.add_user_message(content="Mock_error")
    response2 = await iql_generator.generate_iql(
        question="Mock_question",
        filters=view.list_filters(),
        event_tracker=event_tracker,
        prompt_template=template_after_response,
    )
    template_after_2nd_response = template_after_response.add_assistant_message(content="LLM IQL mock answer")
    assert response2 == ("LLM IQL mock answer", template_after_2nd_response)


@pytest.mark.asyncio
async def test_iql_few_shot_generation(llm: MockLLM, event_tracker: EventTracker, view: MockView) -> None:
    iql_generator = IQLGenerator(llm)

    filters = {str(_filter) for _filter in view.list_filters()}
    assert filters == {"filter_by_id(idx: int)", "filter_by_name(city: str)"}

    input_formatter = IQLInputFormatter(
        question="Mock_question",
        filters=view.list_filters(),
        examples=[FewShotExample("question", "filter_by_id(0)")],
    )
    expected_conversation = input_formatter(IQL_GENERATION_TEMPLATE)

    response = await iql_generator.generate_iql(
        question="Mock_question",
        filters=view.list_filters(),
        examples=[FewShotExample("question", "filter_by_id(0)")],
        event_tracker=event_tracker,
        prompt_template=IQL_GENERATION_TEMPLATE,
    )
    template_after_response = expected_conversation.add_assistant_message(content="LLM IQL mock answer")
    assert response == ("LLM IQL mock answer", template_after_response)

    template_after_response = template_after_response.add_user_message(content="Mock_error")
    response2 = await iql_generator.generate_iql(
        question="Mock_question",
        filters=view.list_filters(),
        event_tracker=event_tracker,
        prompt_template=template_after_response,
    )
    template_after_2nd_response = template_after_response.add_assistant_message(content="LLM IQL mock answer")
    assert response2 == ("LLM IQL mock answer", template_after_2nd_response)
