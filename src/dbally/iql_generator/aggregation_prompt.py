from typing import List

from dbally.exceptions import UnsupportedAggregationError
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


def _validate_agg_response(llm_response: str) -> str:
    """
    Validates LLM response to IQL

    Args:
        llm_response: LLM response

    Returns:
        A string containing aggregations.

    Raises:
        UnsupportedAggregationError: When IQL generator is unable to construct a query
        with given aggregation.
    """
    if "unsupported query" in llm_response.lower():
        raise UnsupportedAggregationError
    return llm_response


class AggregationPromptFormat(PromptFormat):
    """
    Aggregation prompt format, providing a question and aggregation to be used in the conversation.
    """

    def __init__(
        self,
        question: str,
        aggregations: List[ExposedFunction] = None,
    ) -> None:
        super().__init__()
        self.question = question
        self.aggregations = "\n".join([str(aggregation) for aggregation in aggregations]) if aggregations else []


AGGREGATION_GENERATION_TEMPLATE = PromptTemplate[AggregationPromptFormat](
    [
        {
            "role": "system",
            "content": "You have access to an API that lets you query a database supporting a SINGLE aggregation.\n"
            "When prompted for an aggregation, use the following methods: \n"
            "{aggregations}"
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n{aggregations}\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`"""
            "This is CRUCIAL to put `UNSUPPORTED QUERY` text only, otherwise the system will crash. "
            "Structure output to resemble the following pattern:\n"
            'aggregation1("arg1", arg2)\n',
        },
        {"role": "user", "content": "{question}"},
    ],
    response_parser=_validate_agg_response,
)
