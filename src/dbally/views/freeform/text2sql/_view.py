from typing import Iterable, Tuple

import sqlalchemy
from sqlalchemy import text

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.data_models.prompts import PromptTemplate
from dbally.llm_client.base import LLMClient
from dbally.views.base import BaseView

from ._config import Text2SQLConfig
from ._errors import Text2SQLError


class EmptyResultException(Exception):
    """Raised when the result of a query is empty."""


text2sql_prompt = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to the following {dialect} tables:\n"
            "{tables}\n"
            "Create SQL query to answer user question. Return only SQL surrounded in ```sql <QUERY> ``` block.\n",
        },
        {
            "role": "user",
            "content": "{question}\nReturn ONLY the SQL query, with no explanation. Make sure that query "
            "is correct and executable.",
        },
    ),
)

text2sql_cot_prompt = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to the following {dialect} tables:\n"
            "{tables}\n"
            "Perform following tasks:\n"
            "1. Based on the user question, rewrite the tables definition USING SAME FORMAT AS ABOVE leaving"
            "only the columns that may be useful to answer the query.\n"
            # This leads to hallucinations, and it most often selects only columns it will use.
            "2. Think about the solution to the task. Start thinking about what you need to do in FROM and"
            "WHERE statements to answer the question. If any complex processing is required describe it."
            "Make this proces concise and do not generate SQL query yet\n"
            "3. Based on the user question, write the SQL query, with no explanation. Write SQL surrounded"
            "in ```sql <QUERY> ``` block. Make sure that query is correct and executable.\n",
        },
        {
            "role": "user",
            "content": "{question}\n. ",
        },
    ),
)


class Text2SQLFreeformView(BaseView):
    """
    Text2SQLFreeformView is a class designed to interact with the database using text2sql queries.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine, config: Text2SQLConfig) -> None:
        super().__init__()
        self._engine = engine
        self._config = config

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
        conversation = text2sql_cot_prompt
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

    async def _generate_sql(
        self, query: str, conversation: PromptTemplate, llm_client: LLMClient, event_tracker: EventTracker
    ) -> Tuple[str, PromptTemplate]:
        # query_embedding = await self.emb_client.get_embeddings([query])

        # results = self.sim_client.query(
        #     query_embeddings=query_embedding,
        #     n_results=5,
        #     where= {"db_id": {"$ne": self.db_id}}
        # )

        # few_shot_prompt = "/* Some example questions and corresponding
        # SQL queries are provided based on similar problems : */\n"

        # for question, metadata in results["documents"]:
        #     few_shot_prompt += f"/* Answer the following: {question} */\n"
        #     few_shot_prompt += f"{metadata['sql']}\n"

        response = await llm_client.text_generation(
            template=conversation,
            fmt={"tables": self._get_tables_context(), "dialect": self._engine.dialect.name, "question": query},
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
