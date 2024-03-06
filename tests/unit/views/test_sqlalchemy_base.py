# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

import re

import sqlalchemy

from dbally.iql import IQLActions, IQLQuery
from dbally.views.base import ExposedFunction, MethodParamWithTyping
from dbally.views.decorators import view_action, view_filter
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView


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

    @view_action()
    async def action_baz(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        """
        This is baz
        """
        return select.order_by("foo")

    @view_action()
    def action_qux(self, select: sqlalchemy.Select, limit: int) -> sqlalchemy.Select:
        return select.limit(limit)


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
    query = IQLQuery.parse(
        'method_foo(1) and method_bar("London", 2020)',
        allowed_functions=[
            ExposedFunction(
                name="method_foo",
                description="",
                parameters=[
                    MethodParamWithTyping(name="foo", type=int),
                ],
            ),
            ExposedFunction(
                name="method_bar",
                description="",
                parameters=[MethodParamWithTyping(name="city", type=str), MethodParamWithTyping(name="year", type=int)],
            ),
        ],
    )
    await mock_view.apply_filters(query)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).context["sql"])
    assert sql == "SELECT 'test' AS foo WHERE 1 AND 'hello London in 2020'"


async def test_action_sql_generation() -> None:
    """
    Tests that the SQL generation based on actions works correctly
    """
    mock_connection = sqlalchemy.create_mock_engine("postgresql://", executor=None)
    mock_view = MockSqlAlchemyView(mock_connection.engine)
    actions = IQLActions.parse(
        "action_baz()\naction_qux(5)",
        allowed_functions=[
            ExposedFunction(name="action_baz", description="", parameters=[]),
            ExposedFunction(
                name="action_qux", description="", parameters=[MethodParamWithTyping(name="foo", type=int)]
            ),
        ],
    )
    await mock_view.apply_actions(actions)
    sql = normalize_whitespace(mock_view.execute(dry_run=True).context["sql"].replace("\n", ""))
    assert sql == "SELECT 'test' AS foo ORDER BY foo LIMIT 5"
