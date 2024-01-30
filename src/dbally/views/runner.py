import ast
from typing import List

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
        parsed_tree = ast.parse(filters)

        first_element = parsed_tree.body[0]

        if not isinstance(first_element, ast.Expr):
            raise ValueError(f"{first_element} is not a valid python expression")

        self.view.apply_filters(first_element.value)

    def apply_actions(self, actions: str) -> None:
        """
        Applies actions to the view, given as a string of python code
        (may include multiple calls separated by newlines)

        :param actions: String of python code representing the actions to apply

        :raises ValueError: If the given string is not a valid python call
        """
        parsed_tree = ast.parse(actions)
        calls: List[ast.Call] = []

        for element in parsed_tree.body:
            if isinstance(element, ast.Expr) and isinstance(element.value, ast.Call):
                calls.append(element.value)
            else:
                raise ValueError(f"{element} on line {element.lineno} is not a valid python call")

        self.view.apply_actions(calls)

    def generate_sql(self) -> str:
        """
        Generates SQL for the view, based on the applied filters and actions

        :return: Generated SQL
        """
        return self.view.generate_sql()
