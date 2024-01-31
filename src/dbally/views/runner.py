from dbally.iql import IQLActions, IQLQuery
from dbally.views.registry import ViewRegistry, default_registry


class Runner:
    """
    Runner for views, used to apply filters and actions and generate SQL

    :param view_name: Name of the view to run
    :param registry: Registry to use (defaults to the default registry)
    """

    def __init__(self, view_name: str, registry: ViewRegistry = default_registry) -> None:
        self.registry = registry
        self.view_name = view_name
        self.view = self.registry.get(view_name)

    def apply_filters(self, filters: str) -> None:
        """
        Applies filters to the view, given as a string of python code (may include boolean operators)

        :param filters: String of python code representing the filters to apply

        :raises ValueError: If the given string is not a valid python expression
        """
        parsed = IQLQuery.parse(filters)
        self.view.apply_filters(parsed)

    def apply_actions(self, actions: str) -> None:
        """
        Applies actions to the view, given as a string of python code
        (may include multiple calls separated by newlines)

        :param actions: String of python code representing the actions to apply

        :raises ValueError: If the given string is not a valid python call
        """
        parsed = IQLActions.parse(actions)
        self.view.apply_actions(parsed)

    def generate_sql(self) -> str:
        """
        Generates SQL for the view, based on the applied filters and actions

        :return: Generated SQL
        """
        return self.view.generate_sql()
