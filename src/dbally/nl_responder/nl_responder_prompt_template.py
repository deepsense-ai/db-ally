from typing import Any, Dict, List

import pandas as pd

from dbally.prompt import PromptTemplate
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat


def _promptify_results(results: List[Dict]) -> str:
    """
    Formats results into a markdown table.

    Args:
        results: List of results to be formatted.

    Returns:
        Results formatted as a markdown table.
    """
    df = pd.DataFrame.from_records(results)
    return df.to_markdown(index=False, headers="keys", tablefmt="psql")


class NLResponderPromptFormat(PromptFormat):
    """
    IQL prompt format, providing a question and filters to be used in the conversation.
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
        self.results = _promptify_results(results)


default_nl_responder_template = PromptTemplate[NLResponderPromptFormat](
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps answer the user's questions "
            "based on the table provided. You MUST use the table to answer the question. "
            "You are very intelligent and obedient.\n"
            "The table ALWAYS contains full answer to a question.\n"
            "Answer the question in a way that is easy to understand and informative.\n"
            "DON'T MENTION using a table in your answer.",
        },
        {
            "role": "user",
            "content": "The table below represents the answer to a question: {question}.\n"
            "{results}\nAnswer the question: {question}.",
        },
    )
)
