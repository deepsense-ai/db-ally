from abc import ABC, abstractmethod

from dbally.data_models.db_query import QueryResult


class DBConnector(ABC):
    """General interface for the database connections."""

    @abstractmethod
    async def run_query(self, sql_query: str) -> QueryResult:
        """
        Runs the SQL query and returns the result.

        Args:
            sql_query: The SQL query to send to the database.

        Returns:
            QueryResult object containing sql query together with its results and execution time.
        """
