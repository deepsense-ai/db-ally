import abc
import ast
from typing import Callable, List, Tuple

import sqlalchemy

from dbally.views import decorators
from dbally.views.methods_base import MethodsBaseView


class SqlAlchemyBaseView(MethodsBaseView):
    """
    Base class for views that use SQLAlchemy to generate SQL queries.
    """

    def __init__(self) -> None:
        super().__init__()
        self._select = self.get_select()

    @abc.abstractmethod
    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """

    def apply_filters(self, filters: ast.expr) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: AST node representing the filters to apply
        """
        self._select = self._select.where(self._build_filter_node(filters))

    def apply_actions(self, actions: List[ast.Call]) -> None:
        """
        Applies the chosen actions to the view.

        :param actions: List of AST nodes representing the actions to apply
        """
        for action in actions:
            self._select = self._build_action_call(action)

    def generate_sql(self) -> str:
        """
        Generates the SQL query, based on the applied filters and actions.

        :return: Generated SQL
        """
        return str(self._select.compile(compile_kwargs={"literal_binds": True}))

    def _build_filter_node(self, node: ast.expr) -> sqlalchemy.ColumnElement:
        """
        Converts a filter node from the AST to a SQLAlchemy expression.
        """
        if isinstance(node, ast.BoolOp):
            return self._build_filter_bool_op(node)
        if isinstance(node, ast.Call):
            return self._build_filter_call(node)

        raise ValueError(f"Unsupported grammar: {node}")

    def _build_filter_bool_op(self, bool_op: ast.BoolOp) -> sqlalchemy.ColumnElement:
        """
        Converts a boolean operator node from the AST to a SQLAlchemy expression.
        """
        if isinstance(bool_op.op, ast.Not):
            return sqlalchemy.not_(self._build_filter_node(bool_op.values[0]))

        joiner = {ast.Or: sqlalchemy.or_, ast.And: sqlalchemy.and_}[type(bool_op.op)]
        return joiner(*[self._build_filter_node(value) for value in bool_op.values])

    def _method_with_args_from_ast_call(self, call_obj: ast.Call, method_decorator: Callable) -> Tuple[Callable, list]:
        """
        Converts a method call node from the AST to a method object and its arguments.
        """
        func = call_obj.func
        decorator_name = method_decorator.__name__

        if not isinstance(func, ast.Name):
            raise ValueError(f"Incorrect grammar: {call_obj}")

        if not hasattr(self, func.id):
            raise ValueError(f"The {decorator_name} method {func.id} doesn't exists")

        method = getattr(self, func.id)

        if (
            not hasattr(method, "_methodDecorator")
            or method._methodDecorator != method_decorator  # pylint: disable=protected-access
        ):
            raise ValueError(f"The method {func.id} is not decorated with {decorator_name}")

        method_arguments = {n: a for n, a in method.__annotations__.items() if n not in self.HIDDEN_ARGUMENTS}

        if len(call_obj.args) != len(method_arguments):
            print(call_obj.args, method_arguments)
            raise ValueError(f"The {decorator_name} method {func.id} has incorrect number of arguments")

        args = []
        for arg, (_, arg_type) in zip(call_obj.args, method_arguments.items()):
            if not isinstance(arg, ast.Constant):
                raise ValueError(f"The {decorator_name} method {func.id} has incorrect argument type")
            if not isinstance(arg.value, arg_type):
                raise ValueError(f"The {decorator_name} method {func.id} has incorrect argument type")
            args.append(arg.value)

        return method, args

    def _build_filter_call(self, call_obj: ast.Call) -> sqlalchemy.ColumnElement:
        """
        Converts a filter call node from the AST to a SQLAlchemy expression, based on calling
        the corresponding filter method.
        """
        method, args = self._method_with_args_from_ast_call(call_obj, decorators.view_filter)
        return method(*args)

    def _build_action_call(self, action: ast.Call) -> sqlalchemy.Select:
        """
        Converts an action call node from the AST to an modified SQLAlchemy select object, based on calling
        the corresponding action method.
        """
        method, args = self._method_with_args_from_ast_call(action, decorators.view_action)
        return method(self._select, *args)
