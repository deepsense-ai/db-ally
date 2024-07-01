from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Iterator, List, Optional

from sqlalchemy import Column, Connection, Engine, MetaData, Table
from sqlalchemy.sql.ddl import CreateTable
from typing_extensions import Self

from dbally.llms.base import LLM
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.similarity.index import SimilarityIndex
from dbally.views.freeform.text2sql.config import ColumnConfig, TableConfig


class DiscoveryPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default discovery prompt.
    """

    def __init__(
        self,
        *,
        dialect: str,
        table_ddl: str,
        samples: List[Dict[str, Any]],
    ) -> None:
        """
        Constructs a new DiscoveryPromptFormat instance.

        Args:
            dialect: The SQL dialect of the database.
            table_ddl: The DDL of the table.
            samples: The example rows from the table.
        """
        super().__init__()
        self.dialect = dialect
        self.table_ddl = table_ddl
        self.samples = samples


class SimilarityPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default similarity prompt.
    """

    def __init__(self, *, table_summary: str, column_name: str, samples: List[Any]) -> None:
        """
        Constructs a new SimilarityPromptFormat instance.

        Args:
            table_summary: The summary of the table.
            column_name: The name of the column.
            samples: The example values from the column.
        """
        super().__init__()
        self.table_summary = table_summary
        self.column_name = column_name
        self.samples = samples


DISCOVERY_TEMPLATE = PromptTemplate[DiscoveryPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You are a very smart database programmer. "
                "You will be provided with {dialect} table definition and example rows from this table.\n"
                "Create a concise summary of provided table. Do not list the columns."
            ),
        },
        {
            "role": "user",
            "content": "DDL:\n {table_ddl}\n" "EXAMPLE ROWS:\n {samples}",
        },
    ],
)

SIMILARITY_TEMPLATE = PromptTemplate[SimilarityPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "Determine whether to use semantic search based on the given column.\n"
                "Return TRUE when values are categorical, or synonyms may be used (for example department names),\n"
                "or when values are typo-sensitive (for example person or company names).\n"
                "Return FALSE when a search of the values does not make sense and explicit values should be utilized.\n"
                "Return only one of the following options: TRUE or FALSE."
            ),
        },
        {
            "role": "user",
            "content": "TABLE SUMMARY: {table_summary}\n" "COLUMN NAME: {column_name}\n" "EXAMPLE VALUES: {samples}",
        },
    ],
)


class DescriptionExtractionStrategy(ABC):
    """
    Base class for strategies of extracting descriptions from the database.
    """

    @abstractmethod
    async def extract_description(self, table: Table, connection: Connection) -> str:
        """
        Extract the description from the table.

        Args:
            table: The table to extract the description from.
            connection: The connection to the database.

        Returns:
            The extracted description.
        """


class DBCommentsDescriptionExtraction(DescriptionExtractionStrategy):
    """
    Strategy for extracting descriptions from the database comments.
    """

    async def extract_description(self, table: Table, connection: Connection) -> str:
        """
        Extract the description from the table comments.

        Args:
            table: The table to extract the description from.
            connection: The connection to the database.

        Returns:
            The extracted description.
        """
        return table.comment or ""


class LLMSummaryDescriptionExtraction(DescriptionExtractionStrategy):
    """
    Strategy for extracting descriptions from the database using LLM.
    """

    def __init__(self, llm: LLM, engine: Engine, samples_count: int = 5) -> None:
        self.llm = llm
        self.engine = engine
        self.samples_count = samples_count

    async def extract_description(self, table: Table, connection: Connection) -> str:
        """
        Extract the description from the table using LLM.

        Args:
            table: The table to extract the description from.
            connection: The connection to the database.

        Returns:
            The extracted description.
        """
        ddl = self._generate_ddl(table)
        samples = self._fetch_samples(connection, table)

        prompt_format = DiscoveryPromptFormat(
            dialect=self.engine.dialect.name,
            table_ddl=ddl,
            samples=samples,
        )
        formatted_prompt = DISCOVERY_TEMPLATE.format_prompt(prompt_format)

        return await self.llm.generate_text(formatted_prompt)

    def _fetch_samples(self, connection: Connection, table: Table) -> List[Dict[str, Any]]:
        rows = connection.execute(table.select().limit(self.samples_count)).fetchall()

        # The underscore is used by sqlalchemy to avoid conflicts with column names
        # pylint: disable=protected-access
        return [{str(k): v for k, v in dict(row._mapping).items()} for row in rows]

    def _generate_ddl(self, table: Table) -> str:
        return str(CreateTable(table).compile(self.engine))


class SimilarityIndexSelectionStrategy(ABC):
    """
    Base class for strategies of selecting similarity indexes for the columns.
    """

    @abstractmethod
    async def select_index(
        self,
        table: Table,
        column: Column,
        description: str,
        connection: Connection,
    ) -> Optional[SimilarityIndex]:
        """
        Select the similarity index for the column.

        Args:
            table: The table of the column.
            column: The column to select the index for.
            description: The description of the table.
            connection: The connection to the database.

        Returns:
            The similarity index to use for the column or None if no index should be used.
        """


class NoSimilarityIndexSelection(SimilarityIndexSelectionStrategy):
    """
    Strategy for not suggesting any similarity indexes.
    """

    async def select_index(
        self,
        table: Table,
        column: Column,
        description: str,
        connection: Connection,
    ) -> Optional[SimilarityIndex]:
        """
        Select the similarity index for the column.

        Args:
            table: The table of the column.
            column: The column to select the index for.
            description: The description of the table.
            connection: The connection to the database.
        """
        return None


class LLMSuggestedSimilarityIndexSelection(SimilarityIndexSelectionStrategy):
    """
    Strategy for suggesting similarity indexes for the columns using LLM.
    """

    def __init__(
        self,
        llm: LLM,
        index_builder: Callable[[Engine, Table, Column], SimilarityIndex],
        samples_count: int = 5,
    ) -> None:
        self.llm = llm
        self.index_builder = index_builder
        self.samples_count = samples_count

    async def select_index(
        self,
        table: Table,
        column: Column,
        description: str,
        connection: Connection,
    ) -> Optional[SimilarityIndex]:
        """
        Select the similarity index for the column using LLM.

        Args:
            table: The table of the column.
            column: The column to select the index for.
            description: The description of the table.
            connection: The connection to the database.

        Returns:
            The similarity index to use for the column or None if no index should be used.
        """
        samples = self._fetch_samples(
            connection=connection,
            table=table,
            column=column,
        )

        prompt_format = SimilarityPromptFormat(
            table_summary=description,
            column_name=column.name,
            samples=samples,
        )
        formatted_prompt = SIMILARITY_TEMPLATE.format_prompt(prompt_format)

        use_index = await self.llm.generate_text(formatted_prompt)
        return self.index_builder(connection.engine, table, column) if use_index.upper() == "TRUE" else None

    def _fetch_samples(self, connection: Connection, table: Table, column: Column) -> List[Any]:
        values = connection.execute(
            table.select().with_only_columns(column).distinct().limit(self.samples_count)
        ).fetchall()
        return [value[0] for value in values]


class _AutoDiscoveryBuilderBase:
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    """

    def __init__(
        self,
        engine: Engine,
        llm: Optional[LLM] = None,
        blacklist: Optional[List[str]] = None,
        whitelist: Optional[List[str]] = None,
        description_extraction: Optional[DescriptionExtractionStrategy] = None,
        similarity_selection: Optional[SimilarityIndexSelectionStrategy] = None,
    ) -> None:
        self._engine = engine
        self._llm = llm
        self._blacklist = blacklist
        self._whitelist = whitelist
        self._description_extraction = description_extraction or DBCommentsDescriptionExtraction()
        self._similarity_selection = similarity_selection or NoSimilarityIndexSelection()

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
        self._description_extraction = DBCommentsDescriptionExtraction()
        return self

    async def discover(self) -> List[TableConfig]:
        """
        Discover tables in the database and return the configuration object.

        Returns:
            List of tables with their columns and descriptions.
        """
        with self._engine.connect() as connection:
            tables = []
            for table in self._iterate_tables():
                if self._whitelist is not None and table.name not in self._whitelist:
                    continue

                if self._blacklist is not None and table.name in self._blacklist:
                    continue

                description = await self._description_extraction.extract_description(table, connection)

                columns = []
                for column in self._iterate_columns(table):
                    similarity_index = await self._similarity_selection.select_index(
                        table=table,
                        column=column,
                        description=description,
                        connection=connection,
                    )
                    columns.append(
                        ColumnConfig(
                            name=str(column.name),
                            data_type=str(column.type),
                            similarity_index=similarity_index,
                        )
                    )
                tables.append(
                    TableConfig(
                        name=str(table.name),
                        description=description,
                        columns=columns,
                    )
                )
        return tables

    def _iterate_tables(self) -> Iterator[Table]:
        meta = MetaData()
        meta.reflect(bind=self._engine)
        yield from meta.sorted_tables

    @staticmethod
    def _iterate_columns(table: Table) -> Iterator[Column]:
        for column in table.columns.values():
            if column.type.python_type is str:
                yield column


class AutoDiscoveryBuilderWithLLM(_AutoDiscoveryBuilderBase):
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    It extends the base builder with the ability to use LLM for extra tasks.
    """

    def generate_description_by_llm(self, samples_count: int = 5) -> Self:
        """
        Use LLM to generate descriptions for the tables.
        The descriptions are generated based on the table DDL and a configured count of example rows.

        Args:
            samples_count: The number of example rows to use for generating the description.

        Returns:
            The builder instance.
        """
        self._description_extraction = LLMSummaryDescriptionExtraction(
            llm=self._llm,
            engine=self._engine,
            samples_count=samples_count,
        )
        return self

    def suggest_similarity_indexes(
        self,
        index_builder: Callable[[Engine, Table, Column], SimilarityIndex],
        samples_count: int = 5,
    ) -> Self:
        """
        Enable the suggestion of similarity indexes for the columns in the tables.
        The suggestion is based on the generated table descriptions and example values from the column.

        Args:
            index_builder: The function used to build the similarity index.
            samples_count: The number of example values to use for generating the suggestion.

        Returns:
            The builder instance.
        """
        self._similarity_selection = LLMSuggestedSimilarityIndexSelection(
            llm=self._llm,
            index_builder=index_builder,
            samples_count=samples_count,
        )
        return self


class AutoDiscoveryBuilder(_AutoDiscoveryBuilderBase):
    """
    Builder class for configuring the auto-discovery of the database for text2sql freeform view.
    """

    def use_llm(self, llm: LLM) -> AutoDiscoveryBuilderWithLLM:
        """
        Set the LLM client to use for generating descriptions.

        Args:
            llm: The LLM client to use for generating descriptions.

        Returns:
            The builder instance.
        """
        return AutoDiscoveryBuilderWithLLM(
            engine=self._engine,
            llm=llm,
            blacklist=self._blacklist,
            whitelist=self._whitelist,
            description_extraction=self._description_extraction,
            similarity_selection=self._similarity_selection,
        )


def configure_text2sql_auto_discovery(engine: Engine) -> AutoDiscoveryBuilder:
    """
    Create a builder object used to configure the auto-discovery process of the database for text2sql freeform view.

    Args:
        engine: The SQLAlchemy engine object used to connect to the database.

    Returns:
        The builder object used to configure the auto-discovery process.
    """
    return AutoDiscoveryBuilder(engine)
