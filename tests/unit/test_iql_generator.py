# mypy: disable-error-code="empty-body"

from unittest.mock import AsyncMock, Mock, patch

import pytest
import sqlalchemy

from dbally import decorators
from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.prompt import IQL_GENERATION_TEMPLATE, IQLGenerationPromptFormat
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
    llm.generate_text = AsyncMock(return_value="filter_by_id(1)")
    return llm


@pytest.fixture
def event_tracker() -> EventTracker:
    return EventTracker()


@pytest.fixture
def iql_generator(llm: MockLLM) -> IQLGenerator:
    return IQLGenerator(llm)


@pytest.mark.asyncio
async def test_iql_generation(iql_generator: IQLGenerator, event_tracker: EventTracker, view: MockView) -> None:
    filters = view.list_filters()
    prompt_format = IQLGenerationPromptFormat(
        question="Mock_question",
        filters=filters,
    )
    formatted_prompt = IQL_GENERATION_TEMPLATE.format_prompt(prompt_format)

    with patch("dbally.iql.IQLQuery.parse", AsyncMock(return_value="filter_by_id(1)")) as mock_parse:
        iql = await iql_generator.generate_iql(
            question="Mock_question",
            filters=filters,
            event_tracker=event_tracker,
        )
        assert iql == "filter_by_id(1)"
        iql_generator._llm.generate_text.assert_called_once_with(
            prompt=formatted_prompt,
            event_tracker=event_tracker,
            options=None,
        )
        mock_parse.assert_called_once_with(
            source="filter_by_id(1)",
            allowed_functions=filters,
            event_tracker=event_tracker,
        )


@pytest.mark.asyncio
async def test_iql_generation_error_handling(
    iql_generator: IQLGenerator,
    event_tracker: EventTracker,
    view: MockView,
) -> None:
    filters = view.list_filters()

    mock_node = Mock(col_offset=0, end_col_offset=-1)
    errors = [
        IQLError("err1", mock_node, "src1"),
        IQLError("err2", mock_node, "src2"),
        IQLError("err3", mock_node, "src3"),
        IQLError("err4", mock_node, "src4"),
    ]

    with patch("dbally.iql.IQLQuery.parse", AsyncMock(return_value="filter_by_id(1)")) as mock_parse:
        mock_parse.side_effect = errors
        iql = await iql_generator.generate_iql(
            question="Mock_question",
            filters=filters,
            event_tracker=event_tracker,
        )

        assert iql is None
        assert iql_generator._llm.generate_text.call_count == 4
        for i, arg in enumerate(iql_generator._llm.generate_text.call_args_list[1:], start=1):
            assert f"err{i}" in arg[1]["prompt"].chat[-1]["content"]
