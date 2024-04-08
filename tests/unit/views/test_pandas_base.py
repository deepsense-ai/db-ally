# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

import pandas as pd

from dbally.iql import IQLQuery
from dbally.views.decorators import view_filter
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


async def test_filter_or() -> None:
    """
    Test that the filtering the DataFrame with logical OR works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLQuery.parse(
        'filter_city("Berlin") or filter_city("London")',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_BERLIN_OR_LONDON
    assert result.context["filter_mask"].tolist() == [True, False, True, False, True]


async def test_filter_and() -> None:
    """
    Test that the filtering the DataFrame with logical AND works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLQuery.parse(
        'filter_city("Paris") and filter_year(2020)',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_PARIS_2020
    assert result.context["filter_mask"].tolist() == [False, True, False, False, False]


async def test_filter_not() -> None:
    """
    Test that the filtering the DataFrame with logical NOT works correctly
    """
    mock_view = MockDataFrameView(pd.DataFrame.from_records(MOCK_DATA))
    query = await IQLQuery.parse(
        'not (filter_city("Paris") and filter_year(2020))',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    result = mock_view.execute()
    assert result.results == MOCK_DATA_NOT_PARIS_2020
    assert result.context["filter_mask"].tolist() == [True, False, True, True, True]
