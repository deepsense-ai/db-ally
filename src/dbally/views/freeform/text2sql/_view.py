from typing import Callable, Dict, Iterable, List, Optional, Tuple

import sqlalchemy
from sqlalchemy import ColumnClause, Table, text

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.data_models.prompts import PromptTemplate
from dbally.llm_client.base import LLMClient
from dbally.similarity import AbstractSimilarityIndex, SimilarityIndex, SimilarityStore, SimpleSqlAlchemyFetcher
from dbally.views.base import BaseView

from ._config import Text2SQLConfig, Text2SQLSimilarityType
from ._errors import Text2SQLError

text2sql_prompt = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to the following {dialect} tables:\n"
            "{tables}\n"
            "Create SQL query to answer user question. Return only SQL surrounded in ```sql <QUERY> ``` block.\n",
        },
        {"role": "user", "content": "{question}"},
    ),
)


class Text2SQLFreeformView(BaseView):
    """
    Text2SQLFreeformView is a class designed to interact with the database using text2sql queries.
    """

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine,
        config: Text2SQLConfig,
        similarity_store_builders: Optional[Dict[Text2SQLSimilarityType, Callable[[str], SimilarityStore]]] = None,
        similarity_indexes: Optional[Dict[str, Dict[str, SimilarityIndex]]] = None,
    ) -> None:
        super().__init__()
        self._engine = engine
        self._config = config
        self._similarity_indexes = similarity_indexes or {}
        store_builders = similarity_store_builders or {}

        for table_name, column_name, similarity_type in self._config.iterate_similarity_indexes():
            if column_name not in self._similarity_indexes[table_name] and similarity_type in store_builders:
                store_name = f"text2sql-freeform-index_{table_name}_{column_name}"
                store_builder = store_builders[similarity_type]

                default_fetcher = SimpleSqlAlchemyFetcher(
                    sqlalchemy_engine=self._engine,
                    column=ColumnClause(column_name),
                    table=Table(table_name, sqlalchemy.MetaData()),
                )

                self._similarity_indexes[table_name][column_name] = SimilarityIndex(
                    store=store_builder(store_name), fetcher=default_fetcher
                )

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
                sql, conversation = await self._generate_sql(query, conversation, llm_client, event_tracker)

                if dry_run:
                    return ViewExecutionResult(results=[], context={"sql": sql})

                rows = await self._execute_sql(sql)
                break
            except Exception as e:
                conversation = conversation.add_user_message(f"Query is invalid! Error: {e}")
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
    ) -> Tuple[str, PromptTemplate]:
        response = await llm_client.text_generation(
            template=conversation,
            fmt={"tables": self._get_tables_context(), "dialect": self._engine.dialect.name, "question": query},
            event_tracker=event_tracker,
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

    def list_similarity_indexes(self) -> List[AbstractSimilarityIndex]:
        """
        List all similarity indexes used by the view.

        Returns:
            List of similarity indexes.
        """
        return [index for tables in self._similarity_indexes.values() for index in tables.values()]
