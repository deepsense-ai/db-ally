# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

from typing import List
from unittest.mock import Mock

import pytest

from dbally._collection import Collection
from dbally.iql import IQLActions, IQLQuery
from dbally.utils.errors import NoViewFoundError
from dbally.views.base import AbstractBaseView, ExecutionResult, ExposedFunction


class MockViewBase(AbstractBaseView):
    """
    Mock view base class
    """

    def list_filters(self) -> List[ExposedFunction]:
        return []

    def list_actions(self) -> List[ExposedFunction]:
        return []

    def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def apply_actions(self, actions: IQLActions) -> None:
        ...

    def execute(self, dry_run=False) -> ExecutionResult:
        return ExecutionResult(results=[], context={})


class MockView1(MockViewBase):
    """
    Mock view 1
    """


class MockView2(MockViewBase):
    """
    Mock view 2
    """


class MockView3(MockViewBase):
    """
    Mock view 3, a view with default arguments only
    """

    def __init__(self, foo: str = "bar") -> None:
        self.foo = foo
        super().__init__()


class MockViewWithAttributes(MockViewBase):
    """
    Example of a view with non-default arguments
    """

    def __init__(self, foo: str) -> None:
        self.foo = foo
        super().__init__()


@pytest.fixture(name="collection")
def mock_collection() -> Collection:
    """
    Returns a collection with two mock views
    """
    collection = Collection("foo", view_selector=Mock(), iql_generator=Mock(), nl_responder=Mock(), event_handlers=[])
    collection.add(MockView1)
    collection.add(MockView2)
    return collection


def test_list(collection: Collection) -> None:
    """
    Tests that the list method works correctly
    """

    views = collection.list()
    assert len(views) == 2
    assert views["MockView1"] == "Mock view 1"
    assert views["MockView2"] == "Mock view 2"


def test_get(collection: Collection) -> None:
    """
    Tests that the get method works correctly
    """
    assert isinstance(collection.get("MockView1"), MockView1)


def test_get_not_found(collection: Collection) -> None:
    """
    Tests that the get method raises an exception when the view is not found
    """
    try:
        collection.get("Foo")
        assert False
    except NoViewFoundError:
        assert True


def test_add(collection: Collection) -> None:
    """
    Tests that the add method works correctly
    """
    collection.add(MockView3)
    assert len(collection.list()) == 3
    assert isinstance(collection.get("MockView3"), MockView3)


def test_add_custom_name(collection: Collection) -> None:
    """
    Tests that the add method works correctly when a custom name is provided
    """
    collection.add(MockView3, name="Foo")
    assert len(collection.list()) == 3
    assert isinstance(collection.get("Foo"), MockView3)


def test_add_with_builder(collection: Collection) -> None:
    """
    Tests that the add method works correctly when a builder is provided
    """

    def builder():
        return MockViewWithAttributes("bar")

    mocked_builder = Mock(wraps=builder)
    collection.add(MockViewWithAttributes, builder=mocked_builder)
    assert len(collection.list()) == 3

    view = collection.get("MockViewWithAttributes")
    mocked_builder.assert_called_once()
    assert isinstance(view, MockViewWithAttributes)
    assert view.foo == "bar"


def test_error_when_view_already_registered(collection: Collection) -> None:
    """
    Tests that the add method raises an exception when the view is already registered
    """
    try:
        collection.add(MockView1)
        assert False
    except ValueError:
        assert True


def test_error_when_view_with_non_default_args(collection: Collection) -> None:
    """
    Tests that the add method raises an exception when the view has non-default arguments and no builder is provided
    """
    try:
        collection.add(MockViewWithAttributes)
        assert False
    except ValueError:
        assert True
