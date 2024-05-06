from copy import copy
from typing import Iterable, List, Optional, Tuple

import sqlalchemy
from sqlalchemy import text

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.data_models.prompts import PromptTemplate
from dbally.llm_client.base import LLMClient
from dbally.views.base import BaseView

from ._config import Text2SQLConfig
from ._errors import Text2SQLError
from ._exceptions import EmptyResultException
from .columns_selector import BaseSelector
from .value_retriever import ValueRetriever


class Text2SQLFreeformView(BaseView):
    """
    Text2SQLFreeformView is a class designed to interact with the database using text2sql queries.
    """

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine,
        config: Text2SQLConfig,
        prompt: PromptTemplate,
        columns_selector: Optional[BaseSelector] = None,
        few_shot_selector: Optional[BaseSelector] = None,
        value_retriever: Optional[ValueRetriever] = None,
    ) -> None:
        super().__init__()
        # TODO Think if somehow this can be changed into an
        # agentic system taking a list of LLM agents defined in text2sql.agents.py
        self._engine = engine
        self._config = config
        self._prompt = prompt
        self.columns_selector = columns_selector
        self.few_shot_selector = few_shot_selector
        self.value_retriever = value_retriever

    async def ask(
        self,
        query: str,
        llm_client: LLMClient,
        event_tracker: EventTracker,
        n_retries: int = 3,
        dry_run: bool = False,
        retry_if_empty: bool = False,
        raise_exception: bool = False,
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
            retry_if_empty: If True, the query will be retried if the result is empty.
            raise_exception: If True, the function will raise an exception if the query fails after n_retries.

        Returns:
            The result of the query.

        Raises:
            Text2SQLError: If the text2sql query generation fails after n_retries.
            EmptyResultException: If the result of the query is empty.
        """

        # conversation = text2sql_prompt
        conversation = self._prompt
        # conversation = text2sql_where_prompt
        sql, rows = None, None
        exceptions = []

        for i_retr in range(n_retries):
            # We want to catch all exceptions to retry the process.
            # pylint: disable=broad-except
            try:
                sql, conversation = await self._generate_sql(query, conversation, llm_client, event_tracker)

                if dry_run:
                    return ViewExecutionResult(results=[], context={"sql": sql})

                rows = await self._execute_sql(sql)

                if not rows and retry_if_empty:
                    raise EmptyResultException(
                        "Your query returned an empty result! Try to approach the question again."
                    )

                break
            except Exception as e:
                conversation = conversation.add_user_message(f"Query is invalid! Error: {e}")
                exceptions.append(e)
                continue

        if rows is None and raise_exception:
            raise Text2SQLError("Text2SQL query generation failed", exceptions=exceptions) from exceptions[-1]

        if rows is None:
            results = []
        else:
            results = [dict(row._mapping) for row in rows]  # pylint: disable=protected-access

        # The underscore is used by sqlalchemy to avoid conflicts with column names
        # pylint: disable=protected-access
        return ViewExecutionResult(
            results=results,
            context={
                "sql": sql,
                "retried": i_retr,
                "conversation": conversation,
            },
        )

    def _format_tables(self, ddl, selected_columns: List[str]) -> str:
        columns = copy(selected_columns)

        columns.append("PRIMARY")
        columns.append("FOREIGN")

        ddl_splitted = ddl.split("\n")
        lines_to_be_left = ddl_splitted[:3]

        for line in ddl_splitted[3:-2]:
            if any(col in line for col in selected_columns):
                lines_to_be_left.append(line)

        lines_to_be_left.append(ddl_splitted[-2])

        ddl = "\n".join(lines_to_be_left)

        return ddl

    async def _generate_sql(
        self, query: str, conversation: PromptTemplate, llm_client: LLMClient, event_tracker: EventTracker
    ) -> Tuple[str, PromptTemplate]:
        ddl = self._get_tables_context()

        # TODO maybe this should be each splitted to separate agents,
        # We run entire pipeline through small agents and save results of every agent so it is easilt debugable.

        if self.columns_selector is not None:
            selected_columns = self.columns_selector.get_similar(query)
            ddl = self._format_tables(ddl, selected_columns)

        fmt = {"tables": ddl, "dialect": self._engine.dialect.name, "question": query}

        if self.few_shot_selector is not None:
            few_shot = self.few_shot_selector.get_similar(query)
            fmt["few_shot"] = few_shot

        if self.value_retriever is not None:
            matched_values = self.value_retriever.get_values(query)
            fmt["matched_values"] = matched_values

        response = await llm_client.text_generation(
            template=conversation,
            fmt=fmt,
            event_tracker=event_tracker,
            max_tokens=1024,
        )

        conversation = conversation.add_assistant_message(response)

        response = response.split("```sql")[-1].strip("\n")
        response = response.replace("```", "")
        return response, conversation

    async def _execute_sql(self, sql: str) -> Iterable:
        with self._engine.connect() as conn:
            return conn.execute(text(sql)).fetchall()

    def _get_tables_context(self) -> str:
        context = ""
        for table in self._config.tables.values():
            context += f"{table.ddl}\n"

        return context
