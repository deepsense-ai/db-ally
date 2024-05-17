# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

"""
Collection of mock objects for unit tests.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
from unittest.mock import create_autospec

from dbally import NOT_GIVEN, NotGiven
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.iql_prompt_template import IQLPromptTemplate, default_iql_template
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
    def __init__(self, iql: str) -> None:
        self.iql = iql
        super().__init__(llm_client=create_autospec(LLMClient))

    async def generate_iql(self, *_, **__) -> Tuple[str, IQLPromptTemplate]:
        return self.iql, default_iql_template


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
    _options_cls = MockLLMOptions

    def __init__(
        self,
        model_name: str = "gpt-4-mock",
        default_options: Optional[MockLLMOptions] = None,
    ) -> None:
        super().__init__(model_name, default_options)

    async def call(self, *_, **__) -> str:
        return "mock response"
