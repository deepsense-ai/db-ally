import copy
from typing import Dict, List, Optional

import pandas as pd

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.nl_responder.nl_responder_prompt_template import NLResponderPromptTemplate, default_nl_responder_template
from dbally.nl_responder.query_explainer_prompt_template import (
    QueryExplainerPromptTemplate,
    default_query_explainer_template,
)


class NLResponder:
    """Class used to generate natural language response from the database output."""

    # Keys used to extract the query from the context (ordered by priority)
    QUERY_KEYS = ["iql", "sql", "query"]

    def __init__(
        self,
        llm: LLM,
        query_explainer_prompt_template: Optional[QueryExplainerPromptTemplate] = None,
        nl_responder_prompt_template: Optional[NLResponderPromptTemplate] = None,
        max_tokens_count: int = 4096,
    ) -> None:
        """
        Args:
            llm: LLM used to generate natural language response
            query_explainer_prompt_template: template for the prompt used to generate the iql explanation
                if not set defaults to `default_query_explainer_template`
            nl_responder_prompt_template: template for the prompt used to generate the NL response
                if not set defaults to `nl_responder_prompt_template`
            max_tokens_count: maximum number of tokens that can be used in the prompt
        """
        self._llm = llm
        self._nl_responder_prompt_template = nl_responder_prompt_template or copy.deepcopy(
            default_nl_responder_template
        )
        self._query_explainer_prompt_template = query_explainer_prompt_template or copy.deepcopy(
            default_query_explainer_template
        )
        self._max_tokens_count = max_tokens_count

    async def generate_response(
        self,
        result: ViewExecutionResult,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
    ) -> str:
        """
        Uses LLM to generate a response in natural language form.

        Args:
            result: object representing the result of the query execution
            question: user question
            event_tracker: event store used to audit the generation process
            llm_options: options to use for the LLM client.

        Returns:
            Natural language response to the user question.
        """
        rows = _promptify_rows(result.results)

        tokens_count = self._llm.count_tokens(
            messages=self._nl_responder_prompt_template.chat,
            fmt={"rows": rows, "question": question},
        )

        if tokens_count > self._max_tokens_count:
            context = result.context
            query = next((context.get(key) for key in self.QUERY_KEYS if context.get(key)), question)
            llm_response = await self._llm.generate_text(
                template=self._query_explainer_prompt_template,
                fmt={"question": question, "query": query, "number_of_results": len(result.results)},
                event_tracker=event_tracker,
                options=llm_options,
            )

            return llm_response

        llm_response = await self._llm.generate_text(
            template=self._nl_responder_prompt_template,
            fmt={"rows": _promptify_rows(result.results), "question": question},
            event_tracker=event_tracker,
            options=llm_options,
        )
        return llm_response


def _promptify_rows(rows: List[Dict]) -> str:
    """
    Formats rows into a markdown table.

    Args:
        rows: list of rows to be formatted

    Returns:
        str: formatted rows
    """

    df = pd.DataFrame.from_records(rows)

    return df.to_markdown(index=False, headers="keys", tablefmt="psql")
