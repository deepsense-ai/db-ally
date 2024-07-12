from typing import Any, Dict, List, Optional

import pandas as pd

from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate


class NLResponsePromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default NL response prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        results: List[Dict[str, Any]],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new IQLGenerationPromptFormat instance.

        Args:
            question: Question to be asked.
            filters: List of filters exposed by the view.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.results = pd.DataFrame.from_records(results).to_markdown(index=False, headers="keys", tablefmt="psql")


class QueryExplanationPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default query explanation prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        metadata: Dict[str, Any],
        results: List[Dict[str, Any]],
        examples: Optional[List[FewShotExample]] = None,
    ) -> None:
        """
        Constructs a new QueryExplanationPromptFormat instance.

        Args:
            question: Question to be asked.
            context: Context of the query.
            results: List of results returned by the query.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.query = next((metadata.get(key) for key in ("iql", "sql", "query") if metadata.get(key)), question)
        self.number_of_results = len(results)


NL_RESPONSE_TEMPLATE = PromptTemplate[NLResponsePromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that helps answer the user's questions "
                "based on the table provided. You MUST use the table to answer the question. "
                "You are very intelligent and obedient.\n"
                "The table ALWAYS contains full answer to a question.\n"
                "Answer the question in a way that is easy to understand and informative.\n"
                "DON'T MENTION using a table in your answer."
            ),
        },
        {
            "role": "user",
            "content": (
                "The table below represents the answer to a question: {question}.\n"
                "{results}\n"
                "Answer the question: {question}."
            ),
        },
    ],
)

QUERY_EXPLANATION_TEMPLATE = PromptTemplate[QueryExplanationPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that helps describe a table generated by a query "
                "that answers users' question. "
                "You are very intelligent and obedient.\n"
                "Your task is to provide natural language description of the table used by the logical query "
                "to the database.\n"
                "Describe the table in a way that is short and informative.\n"
                "Make your answer as short as possible, start it by infroming the user that the underlying "
                "data is too long to print and then describe the table based on the question and the query.\n"
                "DON'T MENTION using a query in your answer."
            ),
        },
        {
            "role": "user",
            "content": (
                "The query below represents the answer to a question: {question}.\n"
                "Describe the table generated using this query: {query}.\n"
                "Number of results to this query: {number_of_results}."
            ),
        },
    ],
)
