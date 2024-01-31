# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name

import ast
from typing import List

from dbally.views.base import AbstractBaseView, ExposedFunction
from dbally.views.decorators import view
from dbally.views.registry import ViewRegistry, default_registry


class MockViewBase(AbstractBaseView):
    """
    Mock view base class
    """

    def list_filters(self) -> List[ExposedFunction]:
        return []

    def list_actions(self) -> List[ExposedFunction]:
        return []

    def apply_filters(self, filters: ast.expr) -> None:
        ...

    def apply_actions(self, actions: List[ast.Call]) -> None:
        ...

    def generate_sql(self) -> str:
        return "test"


@view()
class MockView1(MockViewBase):
    """
    Mock view 1
    """


@view()
class MockView2(MockViewBase):
    """
    Mock view 2
    """


class MockView3(MockViewBase):
    """
    Mock view 3
    """


def test_list() -> None:
    """
    Tests that the list method works correctly (default registry)
    """
    views = default_registry.list()
    assert len(views) == 2
    assert views["MockView1"] == "Mock view 1"
    assert views["MockView2"] == "Mock view 2"


def test_get() -> None:
    """
    Tests that the get method works correctly (default registry)
    """
    assert isinstance(default_registry.get("MockView1"), MockView1)


def test_get_not_found() -> None:
    """
    Tests that the get method raises an exception when the view is not found (default registry)
    """
    try:
        default_registry.get("Foo")
        assert False
    except KeyError:
        assert True


def test_register() -> None:
    """
    Tests that the register method works correctly  (default registry)
    """
    default_registry.register(MockView3)
    assert len(default_registry.list()) == 3
    assert isinstance(default_registry.get("MockView3"), MockView3)


def test_register_custom_name() -> None:
    """
    Tests that the register method works correctly when a custom name is provided (default registry)
    """
    default_registry.register(MockView3, "Foo")
    assert len(default_registry.list()) == 4
    assert isinstance(default_registry.get("Foo"), MockView3)


def test_custom_registry() -> None:
    """
    Tests that the custom registry works correctly
    """
    registry = ViewRegistry()
    registry.register(MockView1)
    registry.register(MockView3, "Foo")
    assert len(registry.list()) == 2
    print(registry.list())
    assert registry.list()["MockView1"] == "Mock view 1"
    assert registry.list()["Foo"] == "Mock view 3"
    assert isinstance(registry.get("MockView1"), MockView1)
    assert isinstance(registry.get("Foo"), MockView3)
