import abc
from typing import Callable, Optional, Tuple
import time

import sqlalchemy

from dbally.iql import IQLActions, IQLQuery, syntax
from dbally.views import decorators
from dbally.data_models.execution_result import ExecutionResult, ExecutionMetadata
from dbally.views.methods_base import MethodsBaseView


class SqlAlchemyBaseView(MethodsBaseView):
    """
    Base class for views that use SQLAlchemy to generate SQL queries.
    """

    def __init__(self, sqlalchemy_engine: Optional[sqlalchemy.engine.Engine] = None) -> None:
        super().__init__()
        self._select = self.get_select()
        self._sqlalchemy_engine = sqlalchemy_engine

    @abc.abstractmethod
    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """

    def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: IQLQuery object representing the filters to apply
        """
        self._select = self._select.where(self._build_filter_node(filters.root))

    def apply_actions(self, actions: IQLActions) -> None:
        """
        Applies the chosen actions to the view.

        :param actions: IQLActions object representing the actions to apply
        """
        for action in actions:
            self._select = self._build_action_call(action)

    def generate_sql(self) -> str:
        """
        Generates the SQL query, based on the applied filters and actions.

        :return: Generated SQL
        """
        return str(self._select.compile(compile_kwargs={"literal_binds": True}))

    def _build_filter_node(self, node: syntax.Node) -> sqlalchemy.ColumnElement:
        """
        Converts a filter node from the IQLQuery to a SQLAlchemy expression.
        """
        if isinstance(node, syntax.BoolOp):
            return self._build_filter_bool_op(node)
        if isinstance(node, syntax.FunctionCall):
            return self._build_filter_call(node)

        raise ValueError(f"Unsupported grammar: {node}")

    def _build_filter_bool_op(self, bool_op: syntax.BoolOp) -> sqlalchemy.ColumnElement:
        """
        Converts a boolean operator node from the IQL BoolOp to a SQLAlchemy expression.
        """
        return bool_op.match(
            not_=lambda x: sqlalchemy.not_(self._build_filter_node(x.child)),
            and_=lambda x: sqlalchemy.and_(*[self._build_filter_node(child) for child in x.children]),
            or_=lambda x: sqlalchemy.or_(*[self._build_filter_node(child) for child in x.children]),
        )

    def _method_with_args_from_call(
        self, func: syntax.FunctionCall, method_decorator: Callable
    ) -> Tuple[Callable, list]:
        """
        Converts a IQL FunctionCall node to a method object and its arguments.
        """
        decorator_name = method_decorator.__name__

        if not hasattr(self, func.name):
            raise ValueError(f"The {decorator_name} method {func.name} doesn't exists")

        method = getattr(self, func.name)

        if (
            not hasattr(method, "_methodDecorator")
            or method._methodDecorator != method_decorator  # pylint: disable=protected-access
        ):
            raise ValueError(f"The method {func.name} is not decorated with {decorator_name}")

        method_arguments = {n: a for n, a in method.__annotations__.items() if n not in self.HIDDEN_ARGUMENTS}

        if len(func.arguments) != len(method_arguments):
            print(func.arguments, method_arguments)
            raise ValueError(f"The {decorator_name} method {func.name} has incorrect number of arguments")

        args = []
        for arg, (_, arg_type) in zip(func.arguments, method_arguments.items()):
            if not isinstance(arg, arg_type):
                raise ValueError(f"The {decorator_name} method {func.name} has incorrect argument type")
            args.append(arg)

        return method, args

    def _build_filter_call(self, func: syntax.FunctionCall) -> sqlalchemy.ColumnElement:
        """
        Converts a IQL FunctonCall filter to a SQLAlchemy expression, based on calling
        the corresponding filter method.
        """
        method, args = self._method_with_args_from_call(func, decorators.view_filter)
        return method(*args)

    def _build_action_call(self, action: syntax.FunctionCall) -> sqlalchemy.Select:
        """
        Converts an IQL FunctionCall action to a modified SQLAlchemy select object, based on calling
        the corresponding action method.
        """
        method, args = self._method_with_args_from_call(action, decorators.view_action)
        return method(self._select, *args)

    def execute(self) -> ExecutionResult:
        """
        Executes the generated SQL query and returns the results.

        :return: Query results

        :raises ValueError: If no SQLAlchemy engine was provided during initialization
        """
        if self._sqlalchemy_engine is None:
            raise ValueError("No SQLAlchemy engine provided")
        with self._sqlalchemy_engine.connect() as connection:
            time_start = time.time()
            results = connection.execute(self._select)
            delta = time.time() - time_start
            return ExecutionResult(
                # The underscore is used by sqlalchemy to avoid conflicts with column names
                # pylint: disable=protected-access
                results=[dict(row._mapping) for row in results.fetchall()],
                metadata=ExecutionMetadata(
                    query=str(self._select.compile(compile_kwargs={"literal_binds": True})),
                    execution_time=delta,
                    ),
            )
