import abc
import asyncio

import sqlalchemy

from dbally.collection.results import ViewExecutionResult
from dbally.iql import syntax
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.views.methods_base import MethodsBaseView


class SqlAlchemyBaseView(MethodsBaseView):
    """
    Base class for views that use SQLAlchemy to generate SQL queries.
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.Engine) -> None:
        """
        Creates a new instance of the SQL view.

        Args:
            sqlalchemy_engine: SQLAlchemy engine to use for executing the queries.
        """
        super().__init__()
        self.select = self.get_select()
        self._sqlalchemy_engine = sqlalchemy_engine

    @abc.abstractmethod
    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial
        [SqlAlchemy select object
        ](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select)
        which will be used to build the query.
        """

    async def apply_filters(self, filters: IQLFiltersQuery) -> None:
        """
        Applies the chosen filters to the view.

        Args:
            filters: IQLQuery object representing the filters to apply.
        """
        self.select = self.select.where(await self._build_filter_node(filters.root))

    async def apply_aggregation(self, aggregation: IQLAggregationQuery) -> None:
        """
        Applies the chosen aggregation to the view.

        Args:
            aggregation: IQLQuery object representing the aggregation to apply.
        """
        self.select = await self.call_aggregation_method(aggregation.root)

    async def _build_filter_node(self, node: syntax.Node) -> sqlalchemy.ColumnElement:
        """
        Converts a filter node from the IQLQuery to a SQLAlchemy expression.
        """
        if isinstance(node, syntax.BoolOp):
            return await self._build_filter_bool_op(node)
        if isinstance(node, syntax.FunctionCall):
            return await self.call_filter_method(node)

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

    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        """
        Executes the generated SQL query and returns the results.

        Args:
            dry_run: If True, only adds the SQL query to the context field without executing the query.

        Returns:
            Results of the query where `results` will be a list of dictionaries representing retrieved rows or an empty\
            list if `dry_run` is set to `True`. Inside the `context` field the generated sql will be stored.
        """
        results = []
        sql = str(self.select.compile(bind=self._sqlalchemy_engine, compile_kwargs={"literal_binds": True}))

        if not dry_run:
            with self._sqlalchemy_engine.connect() as connection:
                rows = connection.execute(self.select).fetchall()
                # The underscore is used by sqlalchemy to avoid conflicts with column names
                # pylint: disable=protected-access
                results = [dict(row._mapping) for row in rows]

        return ViewExecutionResult(
            results=results,
            context={"sql": sql},
        )
