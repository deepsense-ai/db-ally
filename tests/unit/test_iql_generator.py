# mypy: disable-error-code="empty-body"

from unittest.mock import AsyncMock, call, patch

import pytest
import sqlalchemy

from dbally import decorators
from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator, IQLGeneratorState
from dbally.views.exceptions import IQLGenerationError
from dbally.views.methods_base import MethodsBaseView
from tests.unit.mocks import MockLLM


class MockView(MethodsBaseView):
    def __init__(self) -> None:
        super().__init__(None)

    def get_select(self) -> sqlalchemy.Select:
        ...

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    async def apply_aggregation(self, filters: IQLQuery) -> None:
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
def iql_generator() -> IQLGenerator:
    return IQLGenerator()


@pytest.mark.asyncio
async def test_iql_generation(
    iql_generator: IQLGenerator,
    llm: MockLLM,
    event_tracker: EventTracker,
    view: MockView,
) -> None:
    filters = view.list_filters()
    aggregations = view.list_aggregations()
    examples = view.list_few_shots()

    llm_responses = [
        "decision: true",
        "filter_by_id(1)",
        "decision: true",
        "aggregate_by_id()",
    ]
    iql_parser_responses = [
        "filter_by_id(1)",
        "aggregate_by_id()",
    ]

    llm.generate_text = AsyncMock(side_effect=llm_responses)
    with patch("dbally.iql.IQLQuery.parse", AsyncMock(side_effect=iql_parser_responses)) as mock_parse:
        iql = await iql_generator(
            question="Mock_question",
            filters=filters,
            aggregations=aggregations,
            examples=examples,
            llm=llm,
            event_tracker=event_tracker,
        )
        assert iql == IQLGeneratorState(filters="filter_by_id(1)", aggregation="aggregate_by_id()")
        assert llm.generate_text.call_count == 4
        mock_parse.assert_has_calls(
            [
                call(
                    source="filter_by_id(1)",
                    allowed_functions=filters,
                    event_tracker=event_tracker,
                ),
                call(
                    source="aggregate_by_id()",
                    allowed_functions=aggregations,
                    event_tracker=event_tracker,
                ),
            ]
        )


@pytest.mark.asyncio
async def test_iql_generation_error_escalation_after_max_retires(
    iql_generator: IQLGenerator,
    llm: MockLLM,
    event_tracker: EventTracker,
    view: MockView,
) -> None:
    filters = view.list_filters()
    aggregations = view.list_aggregations()
    examples = view.list_few_shots()

    llm_responses = [
        "decision: true",
        "filter_by_id(1)",
        "filter_by_id(1)",
        "filter_by_id(1)",
        "filter_by_id(1)",
    ]
    iql_parser_responses = [
        IQLError("err1", "src1"),
        IQLError("err2", "src2"),
        IQLError("err3", "src3"),
        IQLError("err4", "src4"),
    ]

    llm.generate_text = AsyncMock(side_effect=llm_responses)
    with patch("dbally.iql.IQLQuery.parse", AsyncMock(side_effect=iql_parser_responses)), pytest.raises(
        IQLGenerationError
    ):
        iql = await iql_generator(
            question="Mock_question",
            filters=filters,
            aggregations=aggregations,
            examples=examples,
            llm=llm,
            event_tracker=event_tracker,
            n_retries=3,
        )

        assert iql is None
        assert llm.generate_text.call_count == 4
        for i, arg in enumerate(llm.generate_text.call_args_list[1:], start=1):
            assert f"err{i}" in arg[1]["prompt"].chat[-1]["content"]


@pytest.mark.asyncio
async def test_iql_generation_response_after_max_retries(
    iql_generator: IQLGenerator,
    llm: MockLLM,
    event_tracker: EventTracker,
    view: MockView,
) -> None:
    filters = view.list_filters()
    aggregations = view.list_aggregations()
    examples = view.list_few_shots()

    llm_responses = [
        "decision: true",
        "filter_by_id(1)",
        "filter_by_id(1)",
        "filter_by_id(1)",
        "filter_by_id(1)",
        "decision: true",
        "aggregate_by_id()",
    ]
    iql_parser_responses = [
        IQLError("err1", "src1"),
        IQLError("err2", "src2"),
        IQLError("err3", "src3"),
        "filter_by_id(1)",
        "aggregate_by_id()",
    ]

    llm.generate_text = AsyncMock(side_effect=llm_responses)
    with patch("dbally.iql.IQLQuery.parse", AsyncMock(side_effect=iql_parser_responses)):
        iql = await iql_generator(
            question="Mock_question",
            filters=filters,
            aggregations=aggregations,
            examples=examples,
            llm=llm,
            event_tracker=event_tracker,
            n_retries=3,
        )

        assert iql == IQLGeneratorState(filters="filter_by_id(1)", aggregation="aggregate_by_id()")
        assert llm.generate_text.call_count == 7
        for i, arg in enumerate(llm.generate_text.call_args_list[2:5], start=1):
            assert f"err{i}" in arg[1]["prompt"].chat[-1]["content"]
