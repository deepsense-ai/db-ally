# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name


from typing import List, Literal, Tuple

import pytest

from dbally.data_models.execution_result import ViewExecutionResult
from dbally.iql import IQLQuery
from dbally.views.decorators import few_shot, view_filter
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

    @few_shot()
    def examples(self):
        return []

    @few_shot()
    def examples_with_query(self, query: str):
        return []

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


def test_list_few_shot() -> None:
    """
    Tests that the list_few_shot method works correctly
    """
    mock_view = MockMethodsBase()
    few_shots = mock_view.list_few_shot()
    assert len(few_shots) == 2
    assert any([f for f in few_shots if f.name == "examples" and not f.parameters])
    assert any(
        [f for f in few_shots if f.name == "examples_with_query" and f.parameters and f.parameters[0].type == str]
    )


def test_invalid_few_shot() -> None:
    """
    Tests that the view cannot be defined when method decorated with few_shot
    does not comply to signature convention (no args or first str arg)
    """

    with pytest.raises(TypeError) as e_info:

        class MockMethodsBaseInvalidFewShot(MethodsBaseView):
            """
            Mock class for testing the MethodsBaseView
            """

            @few_shot()
            def examples_with_query(self, query: int):
                return []

            async def apply_filters(self, filters: IQLQuery) -> None:
                ...

            def execute(self, dry_run: bool = False) -> ViewExecutionResult:
                return ViewExecutionResult(results=[], context={})

    assert (
        str(e_info.value)
        == "Function decorated with `few_shot` need to have first argument of `str` type. See `FewShotSelectorFunc` signature."
    )
