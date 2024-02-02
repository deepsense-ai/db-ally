# mypy: disable-error-code="empty-body"

from typing import Dict, Union

import pytest
import sqlalchemy

from dbally import SqlAlchemyBaseView, decorators
from dbally.data_models.prompts.iql_prompt_template import default_iql_template
from dbally.data_models.prompts.prompt_template import ChatFormat
from dbally.iql_generator.iql_generator import IQLGenerator


class MockLLMClient:
    def generate(self, prompt: Union[str, ChatFormat], response_format: Dict[str, str]) -> str:
        return """{"filters": "LLM IQL mock answer"}"""


class MockView(SqlAlchemyBaseView):
    def get_select(self) -> sqlalchemy.Select:
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
    return MockLLMClient()


def test_iql_generation(llm_client, view):
    iql_generator = IQLGenerator(llm_client, default_iql_template)

    filters_for_prompt, actions_for_prompt = iql_generator._promptify_view(view.list_filters(), view.list_actions())
    filters_in_prompt = set(filters_for_prompt.split("\n"))
    actions_in_prompt = set(actions_for_prompt.split("\n"))

    assert filters_in_prompt == {"filter_by_id(idx: int)", "filter_by_name(city: str)"}
    assert actions_in_prompt == {"sort_by_id()", "group_by_name()"}

    response = iql_generator.generate_iql(view.list_filters(), view.list_actions(), "Mock_question")
    assert response == "LLM IQL mock answer"
