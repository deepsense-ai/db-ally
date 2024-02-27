import copy
from typing import Dict, List, Optional, Sequence, Union

import pandas as pd
from sqlalchemy.engine import RowMapping

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.answer import Answer
from dbally.data_models.prompts.nl_responder_prompt_template import (
    NLResponderPromptTemplate,
    default_nl_responder_template,
)
from dbally.llm_client.base import LLMClient


class NLResponder:
    """Class used to generate natural language response from the database output."""

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_template: Optional[NLResponderPromptTemplate] = None,
    ) -> None:
        """
        Initializes NLResponser class.

        Args:
            llm_client: LLM client used to generate natural language response
            prompt_template: template for the prompt
        """

        self._llm_client = llm_client
        self._prompt_template = prompt_template or copy.deepcopy(default_nl_responder_template)

    async def generate_response(self, answer: Answer, question: str, event_tracker: EventTracker) -> str:
        """
        Uses LLM to generate a response in natural language form.

        Args:
            answer: object representing answer to the user question
            question: user question
            event_tracker: event store used to audit the generation process

        Returns:
            Natural language response to the user question.
        """

        llm_response = await self._llm_client.text_generation(
            template=self._prompt_template,
            fmt={"rows": _promptify_rows(answer.rows), "sql": answer.sql, "question": question},
            event_tracker=event_tracker,
        )
        return llm_response


def _promptify_rows(rows: Union[Sequence[RowMapping], List[Dict]]) -> str:
    """
    Formats rows into a markdown table.

    Args:
        rows: list of rows to be formatted

    Returns:
        str: formatted rows
    """

    df = pd.DataFrame.from_records(rows)
    return df.to_markdown(index=False, headers="keys", tablefmt="psql")
