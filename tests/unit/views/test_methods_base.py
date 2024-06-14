# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name


from typing import List, Literal, Tuple

from dbally.collection.results import ViewExecutionResult
from dbally.iql import IQLQuery
from dbally.views.decorators import view_filter
from dbally.views.exposed_functions import MethodParamWithTyping
from dbally.views.methods_base import MethodsBaseView


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
    def method_bar(self, cities: List[str], year: Literal["2023", "2024"], pairs: List[Tuple[str, int]]) -> str:
        return f"hello {cities} in {year} of {pairs}"

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[], context={})


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
        MethodParamWithTyping("year", Literal["2023", "2024"]),
        MethodParamWithTyping("pairs", List[Tuple[str, int]]),
    ]
    assert (
        str(method_bar) == "method_bar(cities: List[str], year: Literal['2023', '2024'], pairs: List[Tuple[str, int]])"
    )
