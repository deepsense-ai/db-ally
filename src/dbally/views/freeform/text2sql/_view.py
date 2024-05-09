import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import sqlalchemy
from sqlalchemy import text

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.data_models.prompts import PromptTemplate
from dbally.llm_client.base import LLMClient
from dbally.views.base import BaseView

from ._config import Text2SQLConfig
from ._errors import Text2SQLError

text2sql_prompt = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to the following {dialect} tables:\n"
            "{tables}\n"
            "Create SQL query to answer user question. Response with JSON containing following keys:\n\n"
            "- sql: SQL query to answer the question, with parameter :placeholders for user input.\n"
            "- parameters: a list of parameters to be used in the query, represented by maps with the following keys:\n"
            "  - name: the name of the parameter\n"
            "  - value: the value of the parameter\n"
            "  - table: the table the parameter is used with (if any)\n"
            "  - column: the column the parameter is compared to (if any)\n\n"
            "Respond ONLY with the raw JSON response. Don't include any additional text or characters.",
        },
        {"role": "user", "content": "{question}"},
    ),
    response_format={"type": "json_object"},
)


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


class Text2SQLFreeformView(BaseView):
    """
    Text2SQLFreeformView is a class designed to interact with the database using text2sql queries.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine, config: Text2SQLConfig) -> None:
        super().__init__()
        self._engine = engine
        self._config = config

    async def ask(
        self, query: str, llm_client: LLMClient, event_tracker: EventTracker, n_retries: int = 3, dry_run: bool = False
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result. It generates the SQL query from the natural language query and
        executes it against the database. It retries the process in case of errors.

        Args:
            query: The natural language query to execute.
            llm_client: The LLM client used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.

        Returns:
            The result of the query.

        Raises:
            Text2SQLError: If the text2sql query generation fails after n_retries.
        """

        conversation = text2sql_prompt
        sql, rows = None, None
        exceptions = []

        for _ in range(n_retries):
            # We want to catch all exceptions to retry the process.
            # pylint: disable=broad-except
            try:
                sql, parameters, conversation = await self._generate_sql(query, conversation, llm_client, event_tracker)

                if dry_run:
                    return ViewExecutionResult(results=[], context={"sql": sql})

                rows = await self._execute_sql(sql, parameters)
                break
            except Exception as e:
                conversation = conversation.add_user_message(f"Response is invalid! Error: {e}")
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
        self, query: str, conversation: PromptTemplate, llm_client: LLMClient, event_tracker: EventTracker
    ) -> Tuple[str, List[SQLParameterOption], PromptTemplate]:
        response = await llm_client.text_generation(
            template=conversation,
            fmt={"tables": self._get_tables_context(), "dialect": self._engine.dialect.name, "question": query},
            event_tracker=event_tracker,
        )

        conversation = conversation.add_assistant_message(response)
        data = json.loads(response)
        sql = data["sql"]
        parameters = data.get("parameters", [])

        if not isinstance(parameters, list):
            raise ValueError("Parameters should be a list of dictionaries")
        param_objs = [SQLParameterOption.from_dict(param) for param in parameters]

        return sql, param_objs, conversation

    async def _execute_sql(self, sql: str, parameters: List[SQLParameterOption]) -> Iterable:
        param_values = {param.name: param.value for param in parameters}
        with self._engine.connect() as conn:
            return conn.execute(text(sql), param_values).fetchall()

    def _get_tables_context(self) -> str:
        context = ""
        for table in self._config.tables.values():
            context += f"{table.ddl}\n"

        return context
