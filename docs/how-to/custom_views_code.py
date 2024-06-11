# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring, missing-class-docstring, missing-raises-doc
import dbally
import asyncio
from dataclasses import dataclass
from typing import Iterable, Callable, Any
import abc

from dbally import decorators, MethodsBaseView
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.iql import IQLQuery, syntax
from dbally.collection.results import ViewExecutionResult
from dbally.llms.litellm import LiteLLM

@dataclass
class Candidate:
    id: int
    name: str
    position: str
    years_of_experience: int
    country: str


class FilteredIterableBaseView(MethodsBaseView):
    def __init__(self) -> None:
        super().__init__()
        self._filter: Callable[[Any], bool] = lambda x: True

    @abc.abstractmethod
    def get_data(self) -> Iterable:
        """
        Returns the full data to be filtered.
        """

    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        Args:
            filters: IQLQuery object representing the filters to apply
        """
        self._filter = await self.build_filter_node(filters.root)

    async def build_filter_node(self, node: syntax.Node) -> Callable[[Any], bool]:
        """
        Converts a filter node from the IQLQuery to a Python function.

        Args:
            node: IQLQuery node representing the filter or logical operator
        """
        if isinstance(node, syntax.FunctionCall):  # filter
            return await self.call_filter_method(node)
        if isinstance(node, syntax.And):  # logical AND
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return lambda x: all(child(x) for child in children)  # combine children with logical AND
        if isinstance(node, syntax.Or):  # logical OR
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return lambda x: any(child(x) for child in children)  # combine children with logical OR
        if isinstance(node, syntax.Not):  # logical NOT
            child = await self.build_filter_node(node.child)
            return lambda x: not child(x)
        raise ValueError(f"Unsupported grammar: {node}")

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        print(self._filter)
        filtered_data = list(filter(self._filter, self.get_data()))

        return ViewExecutionResult(results=filtered_data, context={})

class CandidateView(FilteredIterableBaseView):
    def get_data(self) -> Iterable:
        return [
            Candidate(1, "John Doe", "Data Scientist", 2, "France"),
            Candidate(2, "Jane Doe", "Data Engineer", 3, "France"),
            Candidate(3, "Alice Smith", "Machine Learning Engineer", 4, "Germany"),
            Candidate(4, "Bob Smith", "Data Scientist", 5, "Germany"),
            Candidate(5, "Janka Jankowska", "Data Scientist", 3, "Poland"),
        ]

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> Callable[[Candidate], bool]:
        """
        Filters candidates with at least `years` of experience.
        """
        return lambda x: x.years_of_experience >= years

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> Callable[[Candidate], bool]:
        """
        Filters candidates that can be considered for a senior data scientist position.
        """
        return lambda x: x.position in ["Data Scientist", "Machine Learning Engineer", "Data Engineer"] and x.years_of_experience >= 3

    @decorators.view_filter()
    def from_country(self, country: str) -> Callable[[Candidate], bool]:
        """
        Filters candidates from a specific country.
        """
        return lambda x: x.country == country

async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    event_handlers = [CLIEventHandler()]
    collection = dbally.create_collection("recruitment", llm, event_handlers=event_handlers)
    collection.add(CandidateView)

    result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())
