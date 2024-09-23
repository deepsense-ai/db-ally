# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

import re
from dataclasses import dataclass
from typing import Union

import sqlalchemy

from dbally.context import BaseCallerContext
from dbally.iql import IQLAggregationQuery, IQLFiltersQuery
from dbally.views.decorators import view_aggregation, view_filter
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView


@dataclass
class SomeTestContext(BaseCallerContext):
    age: int


class MockSqlAlchemyView(SqlAlchemyBaseView):
    """
    Mock class for testing the SqlAlchemyBaseView
    """

    def get_select(self) -> sqlalchemy.Select:
        return sqlalchemy.select(sqlalchemy.literal("test").label("foo"))

    @view_filter()
    def method_foo(self, idx: int) -> sqlalchemy.ColumnElement:
        """
        Some documentation string
        """
        return sqlalchemy.literal(idx)

    @view_filter()
    async def method_bar(self, city: str, year: int) -> sqlalchemy.ColumnElement:
        return sqlalchemy.literal(f"hello {city} in {year}")

    @view_filter()
    async def method_baz(self, age: Union[int, SomeTestContext]) -> sqlalchemy.ColumnElement:
        if isinstance(age, SomeTestContext):
            return sqlalchemy.literal(age.age)
        return sqlalchemy.literal(age)

    @view_aggregation()
    def method_agg(self) -> sqlalchemy.Select:
        """
        Some documentation string
        """
        return self.select.add_columns(sqlalchemy.literal("baz")).group_by(sqlalchemy.literal("baz"))


def normalize_whitespace(s: str) -> str:
    """
    Changes sexquences of whitespace/newlines to a single space
    """
    return re.sub(r"[\s\n]+", " ", s).strip()


async def test_filter_sql_generation() -> None:
    """
    Tests that the SQL generation based on filters works correctly
    """

    mock_connection = sqlalchemy.create_mock_engine("postgresql://", executor=None)
    mock_view = MockSqlAlchemyView(mock_connection.engine)
    query = await IQLFiltersQuery.parse(
        'method_foo(1) and method_bar("London", 2020)',
        allowed_functions=mock_view.list_filters(),
    )
    await mock_view.apply_filters(query)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).metadata["sql"])
    assert sql == "SELECT 'test' AS foo WHERE 1 AND 'hello London in 2020'"


async def test_aggregation_sql_generation() -> None:
    """
    Tests that the SQL generation based on aggregations works correctly
    """

    mock_connection = sqlalchemy.create_mock_engine("postgresql://", executor=None)
    mock_view = MockSqlAlchemyView(mock_connection.engine)
    query = await IQLAggregationQuery.parse(
        "method_agg()",
        allowed_functions=mock_view.list_aggregations(),
    )
    await mock_view.apply_aggregation(query)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).metadata["sql"])
    assert sql == "SELECT 'test' AS foo, 'baz' AS anon_1 GROUP BY 'baz'"


async def test_filter_and_aggregation_sql_generation() -> None:
    """
    Tests that the SQL generation based on filters and aggregations works correctly
    """

    mock_connection = sqlalchemy.create_mock_engine("postgresql://", executor=None)
    mock_view = MockSqlAlchemyView(mock_connection.engine)
    query = await IQLFiltersQuery.parse(
        'method_foo(1) and method_bar("London", 2020)',
        allowed_functions=mock_view.list_filters() + mock_view.list_aggregations(),
    )
    await mock_view.apply_filters(query)
    query = await IQLAggregationQuery.parse(
        "method_agg()",
        allowed_functions=mock_view.list_aggregations(),
    )
    await mock_view.apply_aggregation(query)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).metadata["sql"])
    assert sql == "SELECT 'test' AS foo, 'baz' AS anon_1 WHERE 1 AND 'hello London in 2020' GROUP BY 'baz'"
