# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

from typing import List
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from dbally._collection import Collection
from dbally.iql import IQLQuery
from dbally.iql._exceptions import IQLError
from dbally.utils.errors import NoViewFoundError
from dbally.views.base import AbstractBaseView, ExecutionResult, ExposedFunction


class MockViewBase(AbstractBaseView):
    """
    Mock view base class
    """

    def list_filters(self) -> List[ExposedFunction]:
        return []

    async def apply_filters(self, filters: IQLQuery) -> None:
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
    mocked_builder.assert_called()
    assert mocked_builder.call_count == 2  # one during registration and one during get
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


def test_error_when_view_builder_with_wrong_return_type(collection: Collection) -> None:
    """
    Tests that the add method raises an exception when the view builder returns a wrong type
    """

    def builder():
        return MockView1()

    with pytest.raises(ValueError):
        collection.add(MockViewWithAttributes, builder=builder)


def test_error_when_view_incorrect_builder(collection: Collection) -> None:
    """
    Tests that the add method raises an exception when the the builder itself raises an exception
    """

    def builder():
        raise ValueError("foo")

    with pytest.raises(ValueError):
        collection.add(MockViewWithAttributes, builder=builder)


@pytest.fixture(name="collection_feedback")
def mock_collection_feedback_loop() -> Collection:
    """
    Returns a collection with two mock views
    """
    iql_generator = AsyncMock()
    iql_generator.add_error_msg = Mock(side_effect=["err1", "err2", "err3", "err4"])
    iql_generator.generate_iql = AsyncMock(
        side_effect=[
            ("iql1_f", "iql1_c"),
            ("iql2_f", "iql2_c"),
            ("iql3_f", "iql3_c"),
            ("iql4_f", "iql4_c"),
        ]
    )

    collection = Collection(
        "foo", view_selector=Mock(), iql_generator=iql_generator, nl_responder=Mock(), event_handlers=[]
    )
    collection.add(MockView1)
    return collection


@pytest.mark.asyncio
async def test_ask_feedback_loop(collection_feedback: Collection) -> None:
    """
    Tests that the ask_feedback_loop method works correctly
    """

    mock_node = Mock(col_offset=0, end_col_offset=-1)
    errors = [
        IQLError("err1", mock_node, "src1"),
        IQLError("err2", mock_node, "src2"),
        ValueError("err3"),
        ValueError("err4"),
    ]
    with patch("dbally._collection.IQLQuery.parse") as mock_iql_query:
        mock_iql_query.side_effect = errors

        await collection_feedback.ask("Mock question")

        iql_gen_error: Mock = collection_feedback._iql_generator.add_error_msg  # type: ignore

        iql_gen_error.assert_has_calls(
            [call("iql1_c", [errors[0]]), call("iql2_c", [errors[1]]), call("iql3_c", [errors[2]])]
        )
        assert iql_gen_error.call_count == 3

        iql_gen_gen_iql: Mock = collection_feedback._iql_generator.generate_iql  # type: ignore

        for i, c in enumerate(iql_gen_gen_iql.call_args_list):
            if i > 0:
                assert c[1]["conversation"] == f"err{i}"

        assert iql_gen_gen_iql.call_count == 4