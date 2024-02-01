# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, disallowed-name


from dbally.iql import IQLActions, IQLQuery
from dbally.views.base import MethodParamWithTyping
from dbally.views.decorators import view_action, view_filter
from dbally.views.methods_base import MethodsBaseView


class MockMethodsBase(MethodsBaseView):
    """
    Mock class for testing the MethodsBaseView
    """

    @view_filter()
    def method_foo(self, idx: int) -> None:
        """
        Some documentation string
        """

    @view_filter()
    def method_bar(self, city: str, year: int) -> str:
        return f"hello {city} in {year}"

    @view_action()
    def action_baz(self) -> None:
        """
        This is baz
        """

    @view_action()
    def action_qux(self, idx: int) -> str:
        return f"hello {idx}"

    def apply_filters(self, filters: IQLQuery) -> None:
        ...

    def apply_actions(self, actions: IQLActions) -> None:
        ...

    def generate_sql(self) -> str:
        return "test"


def test_list_filters() -> None:
    """
    Tests that the list_filters method works correctly
    """
    mock_view = MockMethodsBase()
    filters = mock_view.list_filters()
    assert len(filters) == 2
    method_foo = [f for f in filters if f.name == "method_foo"][0]
    assert method_foo.description == "Some documentation string"
    assert method_foo.parameters == [MethodParamWithTyping("idx", int)]
    method_bar = [f for f in filters if f.name == "method_bar"][0]
    assert method_bar.description == ""
    assert method_bar.parameters == [MethodParamWithTyping("city", str), MethodParamWithTyping("year", int)]


def test_list_actions() -> None:
    """
    Tests that the list_actions method works correctly
    """
    mock_view = MockMethodsBase()
    actions = mock_view.list_actions()
    assert len(actions) == 2
    action_baz = [a for a in actions if a.name == "action_baz"][0]
    assert action_baz.description == "This is baz"
    assert action_baz.parameters == []
    action_qux = [a for a in actions if a.name == "action_qux"][0]
    assert action_qux.description == ""
    assert action_qux.parameters == [MethodParamWithTyping("idx", int)]
