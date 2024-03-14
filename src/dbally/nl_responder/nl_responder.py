import copy
from typing import Dict, List, Optional

import pandas as pd

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ExecutionResult
from dbally.data_models.prompts.iql_explainer_prompt_template import (
    IQLExplainerPromptTemplate,
    default_iql_explainer_template,
)
from dbally.data_models.prompts.nl_responder_prompt_template import (
    NLResponderPromptTemplate,
    default_nl_responder_template,
)
from dbally.llm_client.base import LLMClient
from dbally.nl_responder.token_counters import count_tokens_for_huggingface, count_tokens_for_openai


class NLResponder:
    """Class used to generate natural language response from the database output."""

    def __init__(
        self,
        llm_client: LLMClient,
        iql_explainer_prompt_template: Optional[IQLExplainerPromptTemplate] = None,
        nl_responder_prompt_template: Optional[NLResponderPromptTemplate] = None,
        max_tokens_count: int = 4096,
    ) -> None:
        """
        Initializes NLResponser class.

        Args:
            llm_client: LLM client used to generate natural language response
            iql_explainer_prompt_template: template for the prompt used to generate the iql explanation
            nl_responder_prompt_template: template for the prompt used to generate the NL response
            max_tokens_count: maximum number of tokens that can be used in the prompt
        """

        self._llm_client = llm_client
        self._nl_responder_prompt_template = nl_responder_prompt_template or copy.deepcopy(
            default_nl_responder_template
        )
        self._iql_explainer_prompt_template = iql_explainer_prompt_template or copy.deepcopy(
            default_iql_explainer_template
        )
        self._max_tokens_count = max_tokens_count

    async def generate_response(
        self, result: ExecutionResult, question: str, filters: str, event_tracker: EventTracker
    ) -> str:
        """
        Uses LLM to generate a response in natural language form.

        Args:
            result: object representing the result of the query execution
            question: user question
            filters: filters used in the query
            event_tracker: event store used to audit the generation process

        Returns:
            Natural language response to the user question.
        """

        rows = _promptify_rows(result.results)

        if "gpt" in self._llm_client.model_name:
            tokens_count = count_tokens_for_openai(
                messages=self._nl_responder_prompt_template.chat,
                fmt={"rows": rows, "question": question},
                model=self._llm_client.model_name,
            )

        else:
            tokens_count = count_tokens_for_huggingface(
                messages=self._nl_responder_prompt_template.chat,
                fmt={"rows": rows, "question": question},
                model=self._llm_client.model_name,
            )

        if tokens_count > self._max_tokens_count:
            llm_response = await self._llm_client.text_generation(
                template=self._iql_explainer_prompt_template,
                fmt={"question": question, "filters": filters},
                event_tracker=event_tracker,
            )

            return llm_response

        llm_response = await self._llm_client.text_generation(
            template=self._nl_responder_prompt_template,
            fmt={"rows": _promptify_rows(result.results), "question": question},
            event_tracker=event_tracker,
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
