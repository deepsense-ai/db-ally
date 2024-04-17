# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

from typing_extensions import Annotated

from dbally import MethodsBaseView, decorators
from dbally.iql import IQLQuery
from dbally.views.structured import ViewExecutionResult
from tests.unit.mocks import MockSimilarityIndex

index_foo = MockSimilarityIndex("foo")
index_bar = MockSimilarityIndex("bar")


class FooView(MethodsBaseView):
    @decorators.view_filter()
    def method_foo(self, idx: Annotated[str, index_foo]) -> str:
        return f"hello {idx}"

    @decorators.view_filter()
    def method_bar(self, city: Annotated[str, index_foo], year: Annotated[int, index_bar]) -> str:
        return f"hello {city} in {year}"

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[], context={})


class BarView(MethodsBaseView):
    @decorators.view_filter()
    def method_baz(self, person: Annotated[str, index_bar]) -> str:
        return f"hello {person}"

    @decorators.view_filter()
    def method_qux(self, city: str, year: int) -> str:
        """
        Method without Annotated parameters
        """
        return f"hello {city} in {year}"

    async def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[], context={})
