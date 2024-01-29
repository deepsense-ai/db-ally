import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from asyncpg import Connection, Pool

from dbally.data_models.db_query import QueryResult
from dbally.db_connectors.base import DBConnector


class PGSqlConnector(DBConnector):
    """
    DB Connector with Postgres as a backend.
    """

    def __init__(self, connection: Optional[Connection] = None, connection_pool: Optional[Pool] = None):
        if not connection and not connection_pool:
            raise ValueError("Either connection or connection_pool needs to be specified.")

        self._connection = connection
        self._connection_pool = connection_pool

    async def run_query(self, sql_query: str) -> QueryResult:
        """
        Execute query against DB and return response.

        Args:
            sql_query: SQL template.


        Returns:
            QueryResult object.

        Raises:
            Exception: When query fails.
        """

        try:
            async with self._connect() as conn:
                start_time = time.time()
                rows = await conn.fetch(sql_query)
                execution_time = time.time() - start_time

            return QueryResult(sql_query=sql_query, execution_time=execution_time, rows=rows)
        except Exception as exc:
            raise exc

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[Connection]:
        if self._connection:
            yield self._connection
        elif self._connection_pool:
            async with self._connection_pool.acquire() as connection:
                yield connection
