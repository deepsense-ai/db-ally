import asyncio
from dataclasses import dataclass
from functools import reduce
from typing import List, Optional, Union

import pandas as pd

from dbally.collection.results import ViewExecutionResult
from dbally.iql import syntax
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.views.methods_base import MethodsBaseView


@dataclass(frozen=True)
class Aggregation:
    """
    Represents an aggregation to be applied to a Pandas DataFrame.
    """

    column: str
    function: str


@dataclass(frozen=True)
class AggregationGroup:
    """
    Represents an aggregations and groupbys to be applied to a Pandas DataFrame.
    """

    aggregations: Optional[List[Aggregation]] = None
    groupbys: Optional[Union[str, List[str]]] = None


class DataFrameBaseView(MethodsBaseView):
    """
    Base class for views that use Pandas DataFrames to store and filter data.

    The views take a Pandas DataFrame as input and apply filters to it. The filters are defined as methods
    that return a Pandas Series representing a boolean mask to be applied to the DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Creates a new instance of the DataFrame view.

        Args:
            df: Pandas DataFrame with the data to be filtered.
        """
        super().__init__()
        self.df = df
        self._filter_mask: Optional[pd.Series] = None
        self._aggregation_group: AggregationGroup = AggregationGroup()

    async def apply_filters(self, filters: IQLFiltersQuery) -> None:
        """
        Applies the chosen filters to the view.

        Args:
            filters: IQLQuery object representing the filters to apply.
        """
        self._filter_mask = await self._build_filter_node(filters.root)

    async def apply_aggregation(self, aggregation: IQLAggregationQuery) -> None:
        """
        Applies the aggregation of choice to the view.

        Args:
            aggregation: IQLQuery object representing the aggregation to apply.
        """
        self._aggregation_group = await self.call_aggregation_method(aggregation.root)

    async def _build_filter_node(self, node: syntax.Node) -> pd.Series:
        """
        Converts a filter node from the IQLQuery to a Pandas Series representing
        a boolean mask to be applied to the dataframe.

        Args:
            node: IQLQuery node representing the filter or logical operator.

        Returns:
            A boolean mask that can be used to filter the original DataFrame.

        Raises:
            ValueError: If the node type is not supported.
        """
        if isinstance(node, syntax.FunctionCall):
            return await self.call_filter_method(node)
        if isinstance(node, syntax.And):  # logical AND
            children = await asyncio.gather(*[self._build_filter_node(child) for child in node.children])
            return reduce(lambda x, y: x & y, children)
        if isinstance(node, syntax.Or):  # logical OR
            children = await asyncio.gather(*[self._build_filter_node(child) for child in node.children])
            return reduce(lambda x, y: x | y, children)
        if isinstance(node, syntax.Not):
            child = await self._build_filter_node(node.child)
            return ~child
        raise ValueError(f"Unsupported grammar: {node}")

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        """
        Executes the view and returns the results. The results are filtered based on the applied filters.

        Args:
            dry_run: If True, the method will only add `context` field to the `ExecutionResult` with the\
                mask that would be applied to the dataframe.

        Returns:
            ExecutionResult object with the results and the context information with the binary mask.
        """
        results = pd.DataFrame()

        if not dry_run:
            results = self.df
            if self._filter_mask is not None:
                results = results.loc[self._filter_mask]

            if self._aggregation_group.groupbys is not None:
                results = results.groupby(self._aggregation_group.groupbys)

            if self._aggregation_group.aggregations is not None:
                results = results.agg(
                    **{
                        f"{agg.column}_{agg.function}": (agg.column, agg.function)
                        for agg in self._aggregation_group.aggregations
                    }
                )
                results = results.reset_index()

        return ViewExecutionResult(
            results=results.to_dict(orient="records"),
            context={
                "filter_mask": self._filter_mask,
                "groupbys": self._aggregation_group.groupbys,
                "aggregations": self._aggregation_group.aggregations,
            },
        )
