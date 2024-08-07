# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

from dataclasses import dataclass
from typing import List, Literal, Tuple, Union

from dbally.collection.results import ViewExecutionResult
from dbally.context import BaseCallerContext
from dbally.iql import IQLQuery
from dbally.views.decorators import view_filter
from dbally.views.exposed_functions import MethodParamWithTyping
from dbally.views.methods_base import MethodsBaseView


@dataclass
class TestCallerContext(BaseCallerContext):
    """
    Mock class for testing context.
    """

    current_year: Literal["2023", "2024"]


class MockMethodsBase(MethodsBaseView):
    """
    Mock class for testing the MethodsBaseView
    """

    @view_filter()
    def method_foo(self, idx: int) -> None:
        """
        Some documentation string
        """

    @view_filter()
    def method_bar(
        self, cities: List[str], year: Union[Literal["2023", "2024"], TestCallerContext], pairs: List[Tuple[str, int]]
    ) -> str:
        return f"hello {cities} in {year} of {pairs}"

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[], metadata={})


def test_list_filters() -> None:
    """
    Tests that the list_filters method works correctly
    """
    mock_view = MockMethodsBase()
    filters = mock_view.list_filters()
    assert len(filters) == 2
    method_foo = [f for f in filters if f.name == "method_foo"][0]
    assert method_foo.description == "Some documentation string"
    assert method_foo.parameters == [MethodParamWithTyping("idx", int)]
    assert str(method_foo) == "method_foo(idx: int) - Some documentation string"
    method_bar = [f for f in filters if f.name == "method_bar"][0]
    assert method_bar.description == ""
    assert method_bar.parameters == [
        MethodParamWithTyping("cities", List[str]),
        MethodParamWithTyping("year", Union[Literal["2023", "2024"], TestCallerContext]),
        MethodParamWithTyping("pairs", List[Tuple[str, int]]),
    ]
    assert (
        str(method_bar)
        == "method_bar(cities: List[str], year: Literal['2023', '2024'] | AskerContext, pairs: List[Tuple[str, int]])"
    )


async def test_contextualization() -> None:
    mock_view = MockMethodsBase()
    filters = mock_view.list_filters()
    test_context = TestCallerContext("2024")
    mock_view.contextualize_filters(filters, [test_context])

    method_foo = [f for f in filters if f.name == "method_foo"][0]
    assert method_foo.context_class is None
    assert method_foo.context is None

    method_bar = [f for f in filters if f.name == "method_bar"][0]
    assert method_bar.context_class is TestCallerContext
    assert method_bar.context is test_context
