from typing import Any, Dict, Iterator, List, Optional, Tuple

from sqlalchemy import Column, Connection, Engine, MetaData, Table
from sqlalchemy.sql.ddl import CreateTable
from typing_extensions import Self

from dbally.data_models.prompts import PromptTemplate
from dbally.llm_client.base import LLMClient

from ._config import Text2SQLConfig, Text2SQLTableConfig


class _DescriptionExtractionStrategy:
    """
    Base class for strategies of extracting descriptions from the database.
    """


class _DBCommentsDescriptionExtraction(_DescriptionExtractionStrategy):
    """
    Strategy for extracting descriptions from the database comments.
    """


class _LLMSummaryDescriptionExtraction(_DescriptionExtractionStrategy):
    """
    Strategy for extracting descriptions from the database using LLM.
    """

    def __init__(self, example_rows_cnt: int = 5):
        self.example_rows_cnt = example_rows_cnt


class _AutoDiscoveryBuilderBase:
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    """

    _llm_client: Optional[LLMClient]
    _blacklist: Optional[List[str]]
    _whitelist: Optional[List[str]]
    _description_extraction: _DescriptionExtractionStrategy
    _similarity_enabled: bool

    def __init__(
        self,
        engine: Engine,
        blacklist: Optional[List[str]] = None,
        whitelist: Optional[List[str]] = None,
        description_extraction: Optional[_DescriptionExtractionStrategy] = None,
        columns_description: Optional[Dict[str, str]] = None,
        similarity_enabled: bool = False,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self._engine = engine
        self._llm_client = llm_client

        self._blacklist = blacklist
        self._whitelist = whitelist
        self._description_extraction = description_extraction or _DBCommentsDescriptionExtraction()
        self._similarity_enabled = similarity_enabled
        self._columns_description = columns_description

    def with_blacklist(self, blacklist: List[str]) -> Self:
        """
        Set the blacklist of tables to exclude from the auto-discovery.

        Args:
            blacklist: List of table names to exclude from the auto-discovery.

        Returns:
            The builder instance.

        Raises:
            ValueError: If both a whitelist and a blacklist are set.
        """
        if self._whitelist is not None:
            raise ValueError("Cannot have both a blacklist and a whitelist")

        self._blacklist = blacklist
        return self

    def with_whitelist(self, whitelist: List[str]) -> Self:
        """
        Set the whitelist of tables to include in the auto-discovery.

        Args:
            whitelist: List of table names to include in the auto-discovery.

        Returns:
            The builder instance.

        Raises:
            ValueError: If both a whitelist and a blacklist are set.
        """
        if self._blacklist is not None:
            raise ValueError("Cannot have both a blacklist and a whitelist")

        self._whitelist = whitelist
        return self

    def extract_description_from_comments(self) -> Self:
        """
        Use the comments field in the database as a source for the table descriptions.

        Returns:
           The builder instance.
        """
        self._description_extraction = _DescriptionExtractionStrategy()
        return self

    async def discover(self) -> Text2SQLConfig:
        """
        Discover the tables in the database and return the configuration object.

        Returns:
            Text2SQLConfig: The configuration object for the text2sql freeform view.
        """
        return await _Text2SQLAutoDiscovery(
            llm_client=self._llm_client,
            engine=self._engine,
            whitelist=self._whitelist,
            blacklist=self._blacklist,
            description_extraction=self._description_extraction,
            columns_description=self._columns_description,
            similarity_enabled=self._similarity_enabled,
        ).discover()


class AutoDiscoveryBuilderWithLLM(_AutoDiscoveryBuilderBase):
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    It extends the base builder with the ability to use LLM for extra tasks.
    """

    def generate_description_by_llm(self, example_rows_cnt: int = 5) -> Self:
        """
        Use LLM to generate descriptions for the tables.
        The descriptions are generated based on the table DDL and a configured count of example rows.

        Args:
            example_rows_cnt: The number of example rows to use for generating the description.

        Returns:
            The builder instance.
        """
        self._description_extraction = _LLMSummaryDescriptionExtraction(example_rows_cnt)
        return self


class AutoDiscoveryBuilder(_AutoDiscoveryBuilderBase):
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    """

    def use_llm(self, llm_client: LLMClient) -> AutoDiscoveryBuilderWithLLM:
        """
        Set the LLM client to use for generating descriptions.

        Args:
            llm_client: The LLM client to use for generating descriptions.

        Returns:
            The builder instance.
        """
        return AutoDiscoveryBuilderWithLLM(
            engine=self._engine,
            whitelist=self._whitelist,
            blacklist=self._blacklist,
            description_extraction=self._description_extraction,
            similarity_enabled=self._similarity_enabled,
            llm_client=llm_client,
        )


def configure_text2sql_auto_discovery(engine: Engine) -> AutoDiscoveryBuilder:
    """
    This function is used to automatically discover the tables in the database and generate a yaml file with the tables
    and their columns. The yaml file is used to configure the Text2SQLFreeformView in the dbally library.

    Args:
        engine: The SQLAlchemy engine object used to connect to the database.

    Returns:
        The builder object used to configure the auto-discovery process.
    """
    return AutoDiscoveryBuilder(engine)


discovery_template = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": (
                "You are a very smart database programmer. "
                "You will be provided with {dialect} table definition and example rows from this table.\n"
                "Create a concise summary of provided table. Do not list the columns."
            ),
        },
        {"role": "user", "content": "DDL:\n {table_ddl}\nExample rows:\n {example_rows}"},
    ),
)

similarity_template = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": (
                "Determine whether to use SEMANTIC or TRIGRAM search based on the given column.\n"
                "Use SEMANTIC when values are categorical or synonym may be used (for example department names).\n"
                "Use TRIGRAM when values are sensitive to typos and synonyms does not make sense "
                "(for example person or company names).\n"
                "Use NONE when a search of the values does not make sense and explicit values should be utilized.\n"
                "Return only one of the following options: SEMANTIC, TRIGRAM, or NONE."
            ),
        },
        {
            "role": "user",
            "content": "TABLE SUMMARY: {table_summary}\n" "COLUMN_NAME: {column_name}\n" "EXAMPLE_VALUES: {values}",
        },
    )
)


class _Text2SQLAutoDiscovery:
    """
    Class for auto-discovery of the database for text2sql freeform view.
    """

    def __init__(
        self,
        engine: Engine,
        description_extraction: _DescriptionExtractionStrategy,
        whitelist: Optional[List[str]] = None,
        llm_client: Optional[LLMClient] = None,
        blacklist: Optional[List[str]] = None,
        columns_description: Optional[Dict[str, str]] = None,
        similarity_enabled: bool = False,
    ) -> None:
        self._llm_client = llm_client
        self._engine = engine
        self._whitelist = whitelist
        self._blacklist = blacklist
        self._description_extraction = description_extraction
        self._columns_description = columns_description
        self._similarity_enabled = similarity_enabled

    async def discover(self) -> Text2SQLConfig:
        """
        Discover tables in the database and return the configuration object.

        Returns:
            Text2SQLConfig: The configuration object for the text2sql freeform view.

        Raises:
            ValueError: If the description extraction strategy is invalid.
        """

        connection = self._engine.connect()
        tables = {}

        for table_name, table in self._iterate_tables():
            if self._whitelist is not None and table_name not in self._whitelist:
                continue

            if self._blacklist is not None and table_name in self._blacklist:
                continue

            ddl = self._get_table_ddl(table)

            ddl = self._print_column_values(ddl, table, connection)

            if self._columns_description is not None:
                ddl = self._describe_columns(ddl, self._columns_description)

            if isinstance(self._description_extraction, _DBCommentsDescriptionExtraction):
                description = table.comment
            elif isinstance(self._description_extraction, _LLMSummaryDescriptionExtraction):
                example_rows = self._get_example_rows(
                    connection, table, self._description_extraction.example_rows_cnt
                )  # One row of one table is about 1000 characters...
                description = await self._generate_llm_summary(ddl, example_rows)
            else:
                raise ValueError(f"Invalid description extraction strategy: {self._description_extraction}")

            if self._similarity_enabled:
                similarity = await self._suggest_similarity_indexes(connection, description or "", table)
            else:
                similarity = None

            tables[table_name] = Text2SQLTableConfig(ddl=ddl, description=description, similarity=similarity)

        connection.close()

        return Text2SQLConfig(tables)

    async def _suggest_similarity_indexes(
        self, connection: Connection, description: str, table: Table
    ) -> Dict[str, str]:
        if self._llm_client is None:
            raise ValueError("LLM client is required for suggesting similarity indexes.")

        similarity = {}
        for column_name, column in self._iterate_str_columns(table):
            example_values = self._get_column_example_values(connection, table, column)
            similarity_type = await self._llm_client.text_generation(
                template=similarity_template,
                fmt={"table_summary": description, "column_name": column.name, "values": example_values},
            )
            similarity[column_name] = similarity_type

        return similarity

    async def _generate_llm_summary(self, ddl: str, example_rows: List[dict]) -> str:
        if self._llm_client is None:
            raise ValueError("LLM client is required for generating descriptions.")

        return await self._llm_client.text_generation(
            template=discovery_template,
            fmt={"dialect": self._engine.dialect.name, "table_ddl": ddl, "example_rows": example_rows},
        )

    def _print_column_values(self, ddl: str, table: Table, connection: Connection) -> str:
        ddl += "Below columns with limited amount of unique values are listed:\n"
        for column_name, column in self._iterate_str_columns(table):
            example_values = self._get_column_example_values(connection, table, column, n_rows=10)
            if len(set(example_values)) <= 9 or (len(str(example_values)) < 50):
                ddl += f"{column_name}: {example_values}\n"

        return ddl

    def _describe_columns(self, ddl: str, columns_description: Dict[str, str]) -> str:
        """This function is used to describe evert column of the table. It should resolve all disambiguities

        Args:
            ddl: _description_
            table: _description_
            columns_description: _description_

        Returns:
            _description_
        """
        for column in ddl:
            ddl += f"{column}: {columns_description.get(column, 'No description available')}\n"

        return ddl

    def _iterate_tables(self) -> Iterator[Tuple[str, Table]]:
        meta = MetaData()
        meta.reflect(bind=self._engine)
        for table in meta.sorted_tables:
            yield str(table.name), table

    @staticmethod
    def _iterate_str_columns(table: Table) -> Iterator[Tuple[str, Column]]:
        for column in table.columns.values():
            if column.type.python_type is str:
                yield str(column.name), column

    @staticmethod
    def _get_example_rows(connection: Connection, table: Table, n: int = 5) -> List[Dict[str, Any]]:
        rows = connection.execute(table.select().limit(n)).fetchall()

        # The underscore is used by sqlalchemy to avoid conflicts with column names
        # pylint: disable=protected-access
        return [{str(k): v for k, v in dict(row._mapping).items()} for row in rows]

    @staticmethod
    def _get_column_example_values(connection: Connection, table: Table, column: Column, n_rows=5) -> List[Any]:
        example_values = connection.execute(
            table.select().with_only_columns(column).distinct().limit(n_rows)
        ).fetchall()
        return [x[0] for x in example_values]

    def _get_table_ddl(self, table: Table) -> str:
        # TODO Maybe this should return some kind of object that is motified instead of working on simple string?
        ddl = str(CreateTable(table).compile(self._engine))
        return ddl.replace("NOT NULL", "").replace("NULL", "")
