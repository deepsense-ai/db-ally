# pylint: disable=C0301

from typing import List, Optional

from dbally.exceptions import DbAllyError
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


class UnsupportedQueryError(DbAllyError):
    """
    Error raised when IQL generator is unable to construct a query
    with given filters.
    """


def _validate_iql_response(llm_response: str) -> str:
    """
    Validates LLM response to IQL

    Args:
        llm_response: LLM response

    Returns:
        A string containing IQL for filters.

    Raises:
        UnsuppotedQueryError: When IQL generator is unable to construct a query
        with given filters.
    """
    if "unsupported query" in llm_response.lower():
        raise UnsupportedQueryError
    return llm_response


def _decision_iql_response_parser(response: str) -> bool:
    """
    Parses the response from the decision prompt.

    Args:
        response: Response from the LLM.

    Returns:
        True if the response is positive, False otherwise.
    """
    response = response.lower()
    if "decision:" not in response:
        return False

    _, decision = response.split("decision:", 1)
    return "true" in decision


class DecisionPromptFormat(PromptFormat):
    """
    IQL prompt format, providing a question and filters to be used in the conversation.
    """

    def __init__(self, *, question: str, examples: List[FewShotExample] = None) -> None:
        """
        Constructs a new IQLGenerationPromptFormat instance.

        Args:
            question: Question to be asked.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question


class IQLGenerationPromptFormat(PromptFormat):
    """
    IQL prompt format, providing a question and methods to be used in the conversation.
    """

    def __init__(
        self,
        *,
        question: str,
        methods: List[ExposedFunction],
        examples: Optional[List[FewShotExample]] = None,
    ) -> None:
        """
        Constructs a new IQLGenerationPromptFormat instance.

        Args:
            question: Question to be asked.
            methods: List of filters exposed by the view.
            examples: List of examples to be injected into the conversation.
            aggregations: List of aggregations exposed by the view.
        """
        super().__init__(examples)
        self.question = question
        self.methods = "\n".join([str(condition) for condition in methods]) if methods else []


FILTERING_DECISION_TEMPLATE = PromptTemplate[DecisionPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "Given a question, determine whether the answer requires initial data filtering in order to compute it.\n"
                "Initial data filtering is a process in which the result set is reduced to only include the rows "
                "that meet certain criteria specified in the question.\n\n"
                "---\n\n"
                "Follow the following format.\n\n"
                "Question: ${{question}}\n"
                "Hint: ${{hint}}"
                "Reasoning: Let's think step by step in order to ${{produce the decision}}. We...\n"
                "Decision: indicates whether the answer to the question requires initial data filtering. "
                "(Respond with True or False)\n\n"
            ),
        },
        {
            "role": "user",
            "content": (
                "Question: {question}\n"
                "Hint: Look for words indicating data specific features.\n"
                "Reasoning: Let's think step by step in order to "
            ),
        },
    ],
    response_parser=_decision_iql_response_parser,
)

AGGREGATION_DECISION_TEMPLATE = PromptTemplate[DecisionPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "Given a question, determine whether the answer requires computing the aggregation in order to compute it.\n"
                "Aggregation is a process in which the result set is reduced to a single value.\n\n"
                "---\n\n"
                "Follow the following format.\n\n"
                "Question: ${{question}}\n"
                "Reasoning: Let's think step by step in order to ${{produce the decision}}. We...\n"
                "Decision: indicates whether the answer to the question requires initial data filtering. "
                "(Respond with True or False)\n\n"
            ),
        },
        {
            "role": "user",
            "content": ("Question: {question}\n" "Reasoning: Let's think step by step in order to "),
        },
    ],
    response_parser=_decision_iql_response_parser,
)

FILTERS_GENERATION_TEMPLATE = PromptTemplate[IQLGenerationPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You have access to an API that lets you query a database:\n"
                "\n{methods}\n"
                "Suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
                "Remember! Don't give any comments, just the function calls.\n"
                "The output will look like this:\n"
                'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
                "DO NOT INCLUDE arguments names in your response. Only the values.\n"
                "You MUST use only these methods:\n"
                "\n{methods}\n"
                "It is VERY IMPORTANT not to use methods other than those listed above."
                """If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`"""
                "This is CRUCIAL, otherwise the system will crash. "
            ),
        },
        {
            "role": "user",
            "content": "{question}",
        },
    ],
    response_parser=_validate_iql_response,
)

AGGREGATION_GENERATION_TEMPLATE = PromptTemplate[IQLGenerationPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You have access to an API that lets you query a database supporting a SINGLE aggregation.\n"
                "When prompted for an aggregation, use the following methods: \n"
                "{methods}"
                "DO NOT INCLUDE arguments names in your response. Only the values.\n"
                "You MUST use only these methods:\n"
                "\n{methods}\n"
                "It is VERY IMPORTANT not to use methods other than those listed above."
                """If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`"""
                "This is CRUCIAL to put `UNSUPPORTED QUERY` text only, otherwise the system will crash. "
                "Structure output to resemble the following pattern:\n"
                'aggregation1("arg1", arg2)\n'
            ),
        },
        {
            "role": "user",
            "content": "{question}",
        },
    ],
    response_parser=_validate_iql_response,
)
