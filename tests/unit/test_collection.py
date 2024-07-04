# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name, missing-return-type-doc

from typing import List, Tuple, Type
from unittest.mock import AsyncMock, Mock

import pytest
from typing_extensions import Annotated

import dbally
from dbally.collection import Collection
from dbally.collection.exceptions import IndexUpdateError, NoViewFoundError
from dbally.collection.results import ViewExecutionResult
from dbally.iql import IQLQuery
from dbally.iql.syntax import FunctionCall
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping
from tests.unit.mocks import MockIQLGenerator, MockLLM, MockSimilarityIndex, MockViewBase, MockViewSelector


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


class MockViewWithResults(MockViewBase):
    """
    Mock view with results
    """

    def execute(self, dry_run=False) -> ViewExecutionResult:
        return ViewExecutionResult(results=[{"foo": "bar"}], context={"baz": "qux"})

    def list_filters(self) -> List[ExposedFunction]:
        return [ExposedFunction("test_filter", "", [])]

    def get_iql_generator(self, *_, **__) -> MockIQLGenerator:
        return MockIQLGenerator(IQLQuery(FunctionCall("test_filter", []), "test_filter()"))


@pytest.fixture(name="similarity_classes")
def mock_similarity_classes() -> (
    Tuple[MockSimilarityIndex, MockSimilarityIndex, Type[MockViewBase], Type[MockViewBase]]
):
    """
    Returns two similarity indexes and two views with similarity indexes
    """
    foo_index = MockSimilarityIndex("foo")
    bar_index = MockSimilarityIndex("bar")

    class MockViewWithSimilarity(MockViewBase):
        """
        Mock view with similarity index
        """

        def execute(self, dry_run=False) -> ViewExecutionResult:
            return ViewExecutionResult(results=[{"foo": "bar"}], context={"baz": "qux"})

        def list_filters(self) -> List[ExposedFunction]:
            return [
                ExposedFunction(
                    "test_filter",
                    "",
                    [
                        MethodParamWithTyping("dog", Annotated[str, foo_index]),
                        MethodParamWithTyping("cat", Annotated[str, bar_index]),
                    ],
                ),
                ExposedFunction(
                    "second_filter",
                    "",
                    [
                        MethodParamWithTyping("tiger", Annotated[str, bar_index]),
                    ],
                ),
            ]

    class MockViewWithSimilarity2(MockViewBase):
        """
        Mock view with similarity index
        """

        def execute(self, dry_run=False) -> ViewExecutionResult:
            return ViewExecutionResult(results=[{"foo": "bar"}], context={"baz": "qux"})

        def list_filters(self) -> List[ExposedFunction]:
            return [
                ExposedFunction(
                    "test_filter",
                    "",
                    [
                        MethodParamWithTyping("monkey", Annotated[str, foo_index]),
                    ],
                )
            ]

    return foo_index, bar_index, MockViewWithSimilarity, MockViewWithSimilarity2


@pytest.fixture(name="collection")
def mock_collection() -> Collection:
    """
    Returns a collection with two mock views
    """
    collection = dbally.create_collection(
        "foo",
        llm=MockLLM(),
        view_selector=MockViewSelector("MockView1"),
        nl_responder=AsyncMock(),
    )
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

    class ViewWithMockGenerator(MockViewBase):
        def get_iql_generator(self, *_, **__):
            return iql_generator

    collection = Collection("foo", view_selector=Mock(), llm=MockLLM(), nl_responder=Mock(), event_handlers=[])
    collection.add(ViewWithMockGenerator)
    return collection


async def test_ask_view_selection_single_view() -> None:
    """
    Tests that the ask method select view correctly when there is only one view
    """
    collection = Collection(
        "foo",
        view_selector=MockViewSelector(""),
        llm=MockLLM(),
        nl_responder=AsyncMock(),
        event_handlers=[],
    )
    collection.add(MockViewWithResults)

    result = await collection.ask("Mock question")
    assert result.view_name == "MockViewWithResults"
    assert result.results == [{"foo": "bar"}]
    assert result.context == {"baz": "qux", "iql": "test_filter()"}


async def test_ask_view_selection_multiple_views() -> None:
    """
    Tests that the ask method select view correctly when there are multiple views
    """
    collection = Collection(
        "foo",
        view_selector=MockViewSelector("MockViewWithResults"),
        llm=MockLLM(),
        nl_responder=AsyncMock(),
        event_handlers=[],
    )
    collection.add(MockView1)
    collection.add(MockViewWithResults)
    collection.add(MockView2)

    result = await collection.ask("Mock question")
    assert result.view_name == "MockViewWithResults"
    assert result.results == [{"foo": "bar"}]
    assert result.context == {"baz": "qux", "iql": "test_filter()"}


async def test_ask_view_selection_no_views() -> None:
    """
    Tests that the ask method raises an exception when there are no views
    """
    collection = Collection(
        "foo",
        view_selector=MockViewSelector(""),
        llm=MockLLM(),
        nl_responder=AsyncMock(),
        event_handlers=[],
    )

    with pytest.raises(ValueError):
        await collection.ask("Mock question")


def test_get_similarity_indexes(
    similarity_classes: Tuple[MockSimilarityIndex, MockSimilarityIndex, Type[MockViewBase], Type[MockViewBase]],
    collection: Collection,
) -> None:
    """
    Tests that the get_similarity_indexes method works correctly
    """
    (
        foo_index,
        bar_index,
        MockViewWithSimilarity,  # pylint: disable=invalid-name
        MockViewWithSimilarity2,  # pylint: disable=invalid-name
    ) = similarity_classes
    collection.add(MockViewWithSimilarity)
    collection.add(MockViewWithSimilarity2)

    indexes = collection.get_similarity_indexes()
    assert len(indexes) == 2
    assert indexes[foo_index] == [
        ("MockViewWithSimilarity", "test_filter", "dog"),
        ("MockViewWithSimilarity2", "test_filter", "monkey"),
    ]
    assert indexes[bar_index] == [
        ("MockViewWithSimilarity", "test_filter", "cat"),
        ("MockViewWithSimilarity", "second_filter", "tiger"),
    ]


async def test_update_similarity_indexes(
    similarity_classes: Tuple[MockSimilarityIndex, MockSimilarityIndex, Type[MockViewBase], Type[MockViewBase]],
    collection: Collection,
) -> None:
    """
    Tests that the update_similarity_indexes method triggers the update method of the similarity indexes
    """
    (
        foo_index,
        bar_index,
        MockViewWithSimilarity,  # pylint: disable=invalid-name
        MockViewWithSimilarity2,  # pylint: disable=invalid-name
    ) = similarity_classes
    collection.add(MockViewWithSimilarity)
    collection.add(MockViewWithSimilarity2)

    await collection.update_similarity_indexes()
    assert foo_index.update_count == 1
    assert bar_index.update_count == 1


async def test_update_similarity_indexes_error(
    similarity_classes: Tuple[MockSimilarityIndex, MockSimilarityIndex, Type[MockViewBase], Type[MockViewBase]],
    collection: Collection,
) -> None:
    """
    Tests that the update_similarity_indexes method raises an `IndexUpdateError` exception when
    the update method of the similarity indexes raises an exception
    """
    (
        foo_index,
        bar_index,
        MockViewWithSimilarity,  # pylint: disable=invalid-name
        MockViewWithSimilarity2,  # pylint: disable=invalid-name
    ) = similarity_classes
    collection.add(MockViewWithSimilarity)
    collection.add(MockViewWithSimilarity2)

    foo_exception = ValueError("foo")
    foo_index.update = AsyncMock(side_effect=foo_exception)  # type: ignore
    with pytest.raises(IndexUpdateError) as e:
        await collection.update_similarity_indexes()
    assert (
        str(e.value) == "Failed to update similarity indexes for MockViewWithSimilarity.test_filter.dog, "
        "MockViewWithSimilarity2.test_filter.monkey."
    )
    assert e.value.failed_indexes == {
        foo_index: foo_exception,
    }
    assert bar_index.update_count == 1
