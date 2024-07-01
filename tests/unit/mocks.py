# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

"""
Collection of mock objects for unit tests.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Union

from dbally import NOT_GIVEN, NotGiven
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMClient, LLMOptions
from dbally.similarity.index import AbstractSimilarityIndex
from dbally.view_selection.base import ViewSelector
from dbally.views.structured import BaseStructuredView, ExposedFunction, ViewExecutionResult


class MockViewBase(BaseStructuredView):
    """
    Mock view base class
    """

    def list_filters(self) -> List[ExposedFunction]:
        return []

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run=False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[], context={})


class MockIQLGenerator(IQLGenerator):
    def __init__(self, iql: IQLQuery) -> None:
        self.iql = iql
        super().__init__(llm=MockLLM())

    async def generate_iql(self, *_, **__) -> IQLQuery:
        return self.iql


class MockViewSelector(ViewSelector):
    def __init__(self, name: str) -> None:
        self.name = name

    async def select_view(self, *_, **__) -> str:
        return self.name


class MockSimilarityIndex(AbstractSimilarityIndex):
    def __init__(self, name: str):
        self.name = name
        self.update_count = 0

    async def update(self) -> None:
        self.update_count += 1

    async def similar(self, text: str) -> str:
        return text


@dataclass
class MockLLMOptions(LLMOptions):
    mock_property1: Union[int, NotGiven] = NOT_GIVEN
    mock_property2: Union[str, NotGiven] = NOT_GIVEN


class MockLLMClient(LLMClient[MockLLMOptions]):
    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)

    async def call(self, *_, **__) -> str:
        return "mock response"


class MockLLM(LLM[MockLLMOptions]):
    _options_cls = MockLLMOptions

    def __init__(self, default_options: Optional[MockLLMOptions] = None) -> None:
        super().__init__("mock-llm", default_options)

    @cached_property
    def client(self) -> MockLLMClient:
        return MockLLMClient(model_name=self.model_name)
