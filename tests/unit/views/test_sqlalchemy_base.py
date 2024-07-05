# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

import re
from typing import Union

import sqlalchemy

from dbally.context import BaseCallerContext
from dbally.iql import IQLQuery
from dbally.views.decorators import view_filter
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView


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
    query = await IQLQuery.parse(
        'method_foo(1) and method_bar("London", 2020) and method_baz(BaseCallerContext())',
        allowed_functions=mock_view.list_filters(),
        contexts=[SomeTestContext(age=69)],
    )
    await mock_view.apply_filters(query)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).context["sql"])
    assert sql == "SELECT 'test' AS foo WHERE 1 AND 'hello London in 2020' AND 69"
