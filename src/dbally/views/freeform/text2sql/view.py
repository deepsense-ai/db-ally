import json
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import ColumnClause, Engine, MetaData, Table, text

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompt.template import PromptTemplate
from dbally.similarity import AbstractSimilarityIndex, SimpleSqlAlchemyFetcher
from dbally.views.base import BaseView, IndexLocation
from dbally.views.freeform.text2sql.config import TableConfig
from dbally.views.freeform.text2sql.exceptions import Text2SQLError
from dbally.views.freeform.text2sql.prompt import SQL_GENERATION_TEMPLATE, SQLGenerationPromptFormat


@dataclass
class SQLParameterOption:
    """
    A class representing the options for a SQL parameter.
    """

    name: str
    value: str
    table: Optional[str] = None
    column: Optional[str] = None

    # Maybe use pydantic instead of this method?
    # On the other hand, it would introduce a new dependency
    @staticmethod
    def from_dict(data: Dict[str, str]) -> "SQLParameterOption":
        """
        Creates an instance of SQLParameterOption from a dictionary.

        Args:
            data: The dictionary to create the instance from.

        Returns:
            An instance of SQLParameterOption.

        Raises:
            ValueError: If the dictionary is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Paramter data should be a dictionary")

        if "name" not in data or not isinstance(data["name"], str):
            raise ValueError("Parameter name should be a string")

        if "value" not in data or not isinstance(data["value"], str):
            raise ValueError(f"Value for parameter {data['name']} should be a string")

        if "table" in data and data["table"] is not None and not isinstance(data["table"], str):
            raise ValueError(f"Table for parameter {data['name']} should be a string")

        if "column" in data and data["column"] is not None and not isinstance(data["column"], str):
            raise ValueError(f"Column for parameter {data['name']} should be a string")

        return SQLParameterOption(data["name"], data["value"], data.get("table"), data.get("column"))

    async def value_with_similarity(self) -> str:
        """
        Returns the value after passing it through a similarity index if available for the given table and column.

        Returns:
            str: The value after passing it through a similarity index.
        """
        # TODO: Lookup similarity index for the given volumn
        return self.value


class BaseText2SQLView(BaseView, ABC):
    """
    Text2SQLFreeformView is a class designed to interact with the database using text2sql queries.
    """

    def __init__(
        self,
        engine: Engine,
    ) -> None:
        super().__init__()
        self._engine = engine
        self._table_index = {table.name: table for table in self.get_tables()}

    @abstractmethod
    def get_tables(self) -> List[TableConfig]:
        """
        Get the tables used by the view.

        Returns:
            The list of tables used by the view.
        """

    async def ask(
        self,
        query: str,
        llm: LLM,
        event_tracker: EventTracker,
        n_retries: int = 3,
        dry_run: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result. It generates the SQL query from the natural language query and
        executes it against the database. It retries the process in case of errors.

        Args:
            query: The natural language query to execute.
            llm: The LLM used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.
            llm_options: Options to use for the LLM.

        Returns:
            The result of the query.

        Raises:
            Text2SQLError: If the text2sql query generation fails after n_retries.
        """
        sql, rows = None, None
        exceptions = []

        tables = self.get_tables()
        examples = self.list_few_shots()

        prompt_format = SQLGenerationPromptFormat(
            question=query,
            dialect=self._engine.dialect.name,
            tables=tables,
            examples=examples,
        )
        formatted_prompt = SQL_GENERATION_TEMPLATE.format_prompt(prompt_format)

        for _ in range(n_retries + 1):
            # We want to catch all exceptions to retry the process.
            # pylint: disable=broad-except
            try:
                sql, parameters, formatted_prompt = await self._generate_sql(
                    conversation=formatted_prompt,
                    llm=llm,
                    event_tracker=event_tracker,
                    llm_options=llm_options,
                )

                if dry_run:
                    return ViewExecutionResult(results=[], context={"sql": sql})

                rows = await self._execute_sql(sql, parameters, event_tracker=event_tracker)
                break
            except Exception as e:
                formatted_prompt = formatted_prompt.add_user_message(f"Response is invalid! Error: {e}")
                exceptions.append(e)
                continue

        if rows is None:
            raise Text2SQLError("Text2SQL query generation failed", exceptions=exceptions) from exceptions[-1]

        # The underscore is used by sqlalchemy to avoid conflicts with column names
        # pylint: disable=protected-access
        return ViewExecutionResult(
            results=[dict(row._mapping) for row in rows],
            context={
                "sql": sql,
            },
        )

    async def _generate_sql(
        self,
        conversation: PromptTemplate,
        llm: LLM,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
    ) -> Tuple[str, List[SQLParameterOption], PromptTemplate]:
        response = await llm.generate_text(
            prompt=conversation,
            event_tracker=event_tracker,
            options=llm_options,
        )

        conversation = conversation.add_assistant_message(response)
        data = json.loads(response)
        sql = data["sql"]
        parameters = data.get("parameters", [])

        if not isinstance(parameters, list):
            raise ValueError("Parameters should be a list of dictionaries")
        param_objs = [SQLParameterOption.from_dict(param) for param in parameters]

        return sql, param_objs, conversation

    async def _execute_sql(
        self, sql: str, parameters: List[SQLParameterOption], event_tracker: EventTracker
    ) -> Iterable:
        param_values = {}

        for param in parameters:
            if param.table in self._table_index and self._table_index[param.table][param.column].similarity_index:
                similarity_index = self._table_index[param.table][param.column].similarity_index
                param_values[param.name] = await similarity_index.similar(param.value, event_tracker=event_tracker)
            else:
                param_values[param.name] = param.value

        with self._engine.connect() as conn:
            return conn.execute(text(sql), param_values).fetchall()

    def _create_default_fetcher(self, table: str, column: str) -> SimpleSqlAlchemyFetcher:
        return SimpleSqlAlchemyFetcher(
            sqlalchemy_engine=self._engine,
            column=ColumnClause(column),
            table=Table(table, MetaData()),
        )

    def list_similarity_indexes(self) -> Dict[AbstractSimilarityIndex, List[IndexLocation]]:
        """
        List all similarity indexes used by the view.

        Returns:
            Mapping of similarity indexes to their locations in the (view_name, table_name, column_name) format.
        """
        indexes = defaultdict(list)
        for table in self.get_tables():
            for column in table.columns:
                if column.similarity_index:
                    indexes[column.similarity_index].append((self.__class__.__name__, table.name, column.name))
        return indexes
