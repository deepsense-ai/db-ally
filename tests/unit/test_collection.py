# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

from typing import List
from unittest.mock import Mock

import pytest

from dbally._collection import Collection
from dbally.iql import IQLActions, IQLQuery
from dbally.views.base import AbstractBaseView, ExposedFunction


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

    def generate_sql(self) -> str:
        return "test"


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
    Mock view 3
    """


@pytest.fixture(name="collection")
def mock_collection() -> Collection:
    """
    Returns a collection with two mock views
    """
    collection = Collection("foo", view_selector=Mock(), iql_generator=Mock(), event_handlers=[])
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
    except KeyError:
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
    collection.add(MockView3, "Foo")
    assert len(collection.list()) == 3
    assert isinstance(collection.get("Foo"), MockView3)
