# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

from typing import List, Tuple

import pandas as pd

from dbally.iql import IQLFiltersQuery
from dbally.iql._query import IQLAggregationQuery
from dbally.views.decorators import view_aggregation, view_filter
from dbally.views.pandas_base import DataFrameBaseView

MOCK_DATA = [
    {"name": "Alice", "city": "London", "year": 2020, "age": 30},
    {"name": "Bob", "city": "Paris", "year": 2020, "age": 25},
    {"name": "Charlie", "city": "London", "year": 2021, "age": 35},
    {"name": "David", "city": "Paris", "year": 2021, "age": 40},
    {"name": "Eve", "city": "Berlin", "year": 2020, "age": 45},
]

MOCK_DATA_BERLIN_OR_LONDON = [
    {"name": "Alice", "city": "London", "year": 2020, "age": 30},
    {"name": "Charlie", "city": "London", "year": 2021, "age": 35},
    {"name": "Eve", "city": "Berlin", "year": 2020, "age": 45},
]

MOCK_DATA_PARIS_2020 = [
    {"name": "Bob", "city": "Paris", "year": 2020, "age": 25},
]

MOCK_DATA_NOT_PARIS_2020 = [
    {"name": "Alice", "city": "London", "year": 2020, "age": 30},
    {"name": "Charlie", "city": "London", "year": 2021, "age": 35},
    {"name": "David", "city": "Paris", "year": 2021, "age": 40},
    {"name": "Eve", "city": "Berlin", "year": 2020, "age": 45},
]


class MockDataFrameView(DataFrameBaseView):
    """
    Mock class for testing the DataFrameBaseView
    """

    @view_filter()
    def filter_city(self, city: str) -> pd.Series:
        return self.df["city"] == city

    @view_filter()
    def filter_year(self, year: int) -> pd.Series:
        return self.df["year"] == year

    @view_filter()
    def filter_age(self, age: int) -> pd.Series:
        return self.df["age"] == age

    @view_filter()
    def filter_name(self, name: str) -> pd.Series:
        return self.df["name"] == name

    @view_aggregation()
    def mean_age_by_city(self) -> Tuple[str, List[Tuple[str, str]]]:
        return "city", [("age", "mean")]

    @view_aggregation()
    def count_records(self) -> Tuple[str, List[Tuple[str, str]]]:
        return None, [("name", "count")]


async def test_filter_or() -> None:
    """
    Test that the filtering the DataFrame with logical OR works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLFiltersQuery.parse(
        'filter_city("Berlin") or filter_city("London")',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_BERLIN_OR_LONDON
    assert result.context["filter_mask"].tolist() == [True, False, True, False, True]
    assert result.context["groupbys"] is None
    assert result.context["aggregations"] is None


async def test_filter_and() -> None:
    """
    Test that the filtering the DataFrame with logical AND works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLFiltersQuery.parse(
        'filter_city("Paris") and filter_year(2020)',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_PARIS_2020
    assert result.context["filter_mask"].tolist() == [False, True, False, False, False]
    assert result.context["groupbys"] is None
    assert result.context["aggregations"] is None


async def test_filter_not() -> None:
    """
    Test that the filtering the DataFrame with logical NOT works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLFiltersQuery.parse(
        'not (filter_city("Paris") and filter_year(2020))',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_NOT_PARIS_2020
    assert result.context["filter_mask"].tolist() == [True, False, True, True, True]
    assert result.context["groupbys"] is None
    assert result.context["aggregations"] is None


async def test_aggregation() -> None:
    """
    Test that DataFrame aggregation works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLAggregationQuery.parse(
        "count_records()",
        allowed_functions=mock_view.list_aggregations(),
    )
    await mock_view.apply_aggregation(query)
    result = mock_view.execute()
    assert result.results == [
        {"index": "name_count", "name": 5},
    ]
    assert result.context["filter_mask"] is None
    assert result.context["groupbys"] is None
    assert result.context["aggregations"] == [("name", "count")]


async def test_aggregtion_with_groupby() -> None:
    """
    Test that DataFrame aggregation with groupby works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLAggregationQuery.parse(
        "mean_age_by_city()",
        allowed_functions=mock_view.list_aggregations(),
    )
    await mock_view.apply_aggregation(query)
    result = mock_view.execute()
    assert result.results == [
        {"city": "Berlin", "age_mean": 45.0},
        {"city": "London", "age_mean": 32.5},
        {"city": "Paris", "age_mean": 32.5},
    ]
    assert result.context["filter_mask"] is None
    assert result.context["groupbys"] == "city"
    assert result.context["aggregations"] == [("age", "mean")]


async def test_filters_and_aggregtion() -> None:
    """
    Test that DataFrame filtering and aggregation works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLFiltersQuery.parse(
        "filter_city('Paris')",
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    query = await IQLAggregationQuery.parse(
        "mean_age_by_city()",
        allowed_functions=mock_view.list_aggregations(),
    )
    await mock_view.apply_aggregation(query)
    result = mock_view.execute()
    assert result.results == [{"city": "Paris", "age_mean": 32.5}]
    assert result.context["filter_mask"].tolist() == [False, True, False, True, False]
    assert result.context["groupbys"] == "city"
    assert result.context["aggregations"] == [("age", "mean")]
