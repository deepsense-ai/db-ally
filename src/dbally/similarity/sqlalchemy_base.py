import abc
from typing import List, Optional

import sqlalchemy
from sqlalchemy.sql.elements import ColumnClause

from dbally.similarity.fetcher import SimilarityFetcher
from dbally.similarity.store import SimilarityStore


class SqlAlchemyFetcher(SimilarityFetcher):
    """
    Fetches the data from the database using SQLAlchemy.
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine) -> None:
        self.sqlalchemy_engine = sqlalchemy_engine

    @abc.abstractmethod
    def get_query(self) -> sqlalchemy.Select:
        """
        Returns query that will be used to fetch the data from the database. Should include a single text column.

        Returns:
            sqlalchemy.Select: The query to fetch the data.
        """

    async def fetch(self) -> List[str]:
        """
        Fetches the data from the source and returns it as a list of strings.

        Returns:
            The fetched data.
        """
        with self.sqlalchemy_engine.connect() as conn:
            result = conn.execute(self.get_query())
            return [row[0] for row in result]

    def __repr__(self) -> str:
        """
        Returns a string representation of the fetcher.

        Returns:
            str: The string representation of the fetcher.
        """
        return f"{self.__class__.__name__}()"


class SimpleSqlAlchemyFetcher(SqlAlchemyFetcher):
    """
    Fetches the data from a single column in the database.
    """

    def __init__(
        self, sqlalchemy_engine: sqlalchemy.engine.Engine, column: ColumnClause, table: sqlalchemy.Table
    ) -> None:
        super().__init__(sqlalchemy_engine)
        self.column = column
        self.table = table

    def get_query(self) -> sqlalchemy.Select:
        """
        Returns query that will be used to fetch the data from the database.

        Returns:
            The query to fetch the data.
        """
        return sqlalchemy.select(self.column).select_from(self.table).distinct()

    def __repr__(self) -> str:
        """
        Returns a string representation of the fetcher.

        Returns:
            str: The string representation of the fetcher.
        """
        return f"{self.__class__.__name__}(table={self.table.name}, column={self.column.name})"


class AbstractSqlAlchemyStore(SimilarityStore, metaclass=abc.ABCMeta):
    """
    Stores the data in the database using SQLAlchemy.
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine, table_name: str, threshold: float = 0.8) -> None:
        self.sqlalchemy_engine = sqlalchemy_engine
        self.table_name = table_name
        self.table = sqlalchemy.Table(table_name, sqlalchemy.MetaData(), sqlalchemy.Column("text", sqlalchemy.String))
        self.threshold = threshold

    async def store(self, data: List[str]) -> None:
        """
        Stores the data. Should replace the previously stored data.

        Args:
            data: The data to store.
        """
        # Create the table if it doesn't exist
        self.table.create(self.sqlalchemy_engine, checkfirst=True)

        # Insert the data
        with self.sqlalchemy_engine.connect() as conn:
            conn.execute(self.table.delete())
            conn.execute(self.table.insert(), [{"text": text} for text in data])
            conn.commit()


class CaseInsensitiveSqlAlchemyStore(AbstractSqlAlchemyStore):
    """
    Stores the data in the database using SQLAlchemy and defines "similarity" as case-insensitive equality.
    """

    async def find_similar(self, text: str) -> Optional[str]:
        """
        Finds the text from the store that differs from the given text only in case.

        Args:
            text: The text to find similar to.

        Returns:
            The most similar text or None if no similar text is found.
        """
        with self.sqlalchemy_engine.connect() as conn:
            result = conn.execute(sqlalchemy.select(self.table.c.text).where(self.table.c.text.ilike(text)))
            row = result.fetchone()
            return row[0] if row else None
