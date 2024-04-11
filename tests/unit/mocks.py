# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

"""
Collection of mock objects for unit tests.
"""

from typing import List, Tuple
from unittest.mock import create_autospec

from dbally.data_models.prompts.iql_prompt_template import IQLPromptTemplate, default_iql_template
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.llm_client.base import LLMClient
from dbally.similarity.index import AbstractSimilarityIndex
from dbally.view_selection.base import ViewSelector
from dbally.views.base import AbstractBaseView, ExposedFunction, ViewExecutionResult


class MockViewBase(AbstractBaseView):
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


class MockLLMClient(LLMClient):
    # TODO: Start calling super().__init__ and remove the pyling comment below
    # as soon as the base class is refactored to not have PromptBuilder initialization
    # hardcoded in its constructor.
    # See: DBALLY-105
    # pylint: disable=super-init-not-called
    def __init__(self, *_, **__) -> None:
        self.model_name = "mock model"

    async def text_generation(self, *_, **__) -> str:
        return "mock response"

    async def call(self, *_, **__) -> str:
        return "mock response"
