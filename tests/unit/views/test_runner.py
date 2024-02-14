from unittest.mock import Mock

from dbally._collection import Collection
from dbally.views.runner import Runner
from tests.unit.views.test_sqlalchemy_base import MockSqlAlchemyView


def test_runner() -> None:
    """
    Tests that the runner works correctly
    """
    collection = Collection("foo", iql_generator=Mock(), view_selector=Mock(), event_handlers=[])
    collection.add(MockSqlAlchemyView)
    runner = Runner("MockSqlAlchemyView", collection)
    runner.apply_filters("method_foo(1) and method_bar('London', 2020)")
    runner.apply_actions("action_baz()\naction_qux(5)")
    sql = runner.generate_sql().replace("\n", "")
    assert sql == "SELECT 'test' AS foo WHERE 1 AND 'hello London in 2020' ORDER BY foo LIMIT 5"
