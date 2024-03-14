import abc
import asyncio
import inspect
import time
from typing import Callable, Tuple

import sqlalchemy

from dbally.data_models.execution_result import ExecutionResult
from dbally.iql import IQLQuery, syntax
from dbally.views import decorators
from dbally.views.methods_base import MethodsBaseView


class SqlAlchemyBaseView(MethodsBaseView):
    """
    Base class for views that use SQLAlchemy to generate SQL queries.
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine) -> None:
        super().__init__()
        self._select = self.get_select()
        self._sqlalchemy_engine = sqlalchemy_engine

    @abc.abstractmethod
    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """

    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        :param filters: IQLQuery object representing the filters to apply
        """
        self._select = self._select.where(await self._build_filter_node(filters.root))

    async def _build_filter_node(self, node: syntax.Node) -> sqlalchemy.ColumnElement:
        """
        Converts a filter node from the IQLQuery to a SQLAlchemy expression.
        """
        if isinstance(node, syntax.BoolOp):
            return await self._build_filter_bool_op(node)
        if isinstance(node, syntax.FunctionCall):
            return await self._build_filter_call(node)

        raise ValueError(f"Unsupported grammar: {node}")

    async def _build_filter_bool_op(self, bool_op: syntax.BoolOp) -> sqlalchemy.ColumnElement:
        """
        Converts a boolean operator node from the IQL BoolOp to a SQLAlchemy expression.
        """
        alchemy_op = bool_op.match(
            not_=lambda x: sqlalchemy.not_,
            and_=lambda x: sqlalchemy.and_,
            or_=lambda x: sqlalchemy.or_,
        )

        if hasattr(bool_op, "children"):
            nodes = asyncio.gather(*[self._build_filter_node(child) for child in bool_op.children])
            return alchemy_op(*await nodes)
        if hasattr(bool_op, "child"):
            return alchemy_op(await self._build_filter_node(bool_op.child))
        raise ValueError(f"BoolOp {bool_op} has no children")

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

        return method, func.arguments

    async def _build_filter_call(self, func: syntax.FunctionCall) -> sqlalchemy.ColumnElement:
        """
        Converts a IQL FunctonCall filter to a SQLAlchemy expression, based on calling
        the corresponding filter method.
        """
        method, args = self._method_with_args_from_call(func, decorators.view_filter)

        if inspect.iscoroutinefunction(method):
            return await method(*args)
        return method(*args)

    def execute(self, dry_run: bool = False) -> ExecutionResult:
        """
        Executes the generated SQL query and returns the results.

        :param dry_run: If True, only generate the query without executing it

        :return: Query results

        :raises ValueError: If no SQLAlchemy engine was provided during initialization
        """
        if self._sqlalchemy_engine is None:
            raise ValueError("No SQLAlchemy engine provided")

        results = []
        execution_time = None
        sql = str(self._select.compile(bind=self._sqlalchemy_engine, compile_kwargs={"literal_binds": True}))

        if not dry_run:
            time_start = time.time()
            with self._sqlalchemy_engine.connect() as connection:
                # The underscore is used by sqlalchemy to avoid conflicts with column names
                # pylint: disable=protected-access
                rows = connection.execute(self._select).fetchall()
                results = [dict(row._mapping) for row in rows]
            execution_time = time.time() - time_start

        return ExecutionResult(
            results=results,
            execution_time=execution_time,
            context={"sql": sql},
        )
