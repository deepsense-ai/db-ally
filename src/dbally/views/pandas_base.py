import asyncio
import time
from functools import reduce

import pandas as pd

from dbally.data_models.execution_result import ExecutionResult
from dbally.iql import IQLQuery, syntax
from dbally.views.methods_base import MethodsBaseView


class DataFrameBaseView(MethodsBaseView):
    """
    Base class for views that use Pandas DataFrames to store and filter data.

    The views take a Pandas DataFrame as input and apply filters to it. The filters are defined as methods
    that return a Pandas Series representing a boolean mask to be applied to the DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initializes the view with the input DataFrame.

        :param df: Pandas DataFrame with the data to be filtered
        """
        super().__init__()
        self.df = df

        # The mask to be applied to the dataframe to filter the data
        self._filter_mask: pd.Series = None

    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: IQLQuery object representing the filters to apply
        """
        self._filter_mask = await self.build_filter_node(filters.root)

    async def build_filter_node(self, node: syntax.Node) -> pd.Series:
        """
        Converts a filter node from the IQLQuery to a Pandas Series representing
        boolean mask to be applied to the dataframe.

        :param node: IQLQuery node representing the filter or logical operator

        :return: Pandas Series representing the boolean mask

        :raises ValueError: If the node type is not supported
        """
        if isinstance(node, syntax.FunctionCall):
            return await self.call_filter_method(node)
        if isinstance(node, syntax.And):  # logical AND
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return reduce(lambda x, y: x & y, children)
        if isinstance(node, syntax.Or):  # logical OR
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return reduce(lambda x, y: x | y, children)
        if isinstance(node, syntax.Not):
            child = await self.build_filter_node(node.child)
            return ~child
        raise ValueError(f"Unsupported grammar: {node}")

    def execute(self, dry_run: bool = False) -> ExecutionResult:
        """
        Executes the view and returns the results. The results are filtered based on the applied filters.

        :param dry_run: If True, the method will only return the mask that would be applied to the dataframe

        :return: ExecutionResult object with the results and context information
        """
        start_time = time.time()
        filtered_data = pd.DataFrame.empty

        if not dry_run:
            filtered_data = self.df
            if self._filter_mask is not None:
                filtered_data = filtered_data.loc[self._filter_mask]

        return ExecutionResult(
            results=filtered_data.to_dict(orient="records"),
            execution_time=time.time() - start_time,
            context={
                "filter_mask": self._filter_mask,
            },
        )
