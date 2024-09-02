# pylint: disable=C0301

from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.exceptions import DbAllyError
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


class UnsupportedQueryError(DbAllyError):
    """
    Error raised when IQL generator is unable to construct a query
    with given filters.
    """


async def _iql_filters_parser(
    response: str,
    allowed_functions: List[ExposedFunction],
    event_tracker: Optional[EventTracker] = None,
) -> IQLFiltersQuery:
    """
    Parses the response from the LLM to IQL.

    Args:
        response: LLM response.
        allowed_functions: List of functions that can be used in the IQL.
        event_tracker: Event tracker to be used for auditing.

    Returns:
        IQL query for filters.

    Raises:
        UnsuppotedQueryError: When IQL generator is unable to construct a query with given filters.
    """
    if "unsupported query" in response.lower():
        raise UnsupportedQueryError

    return await IQLFiltersQuery.parse(
        source=response,
        allowed_functions=allowed_functions,
        event_tracker=event_tracker,
    )


async def _iql_aggregation_parser(
    response: str,
    allowed_functions: List[ExposedFunction],
    event_tracker: Optional[EventTracker] = None,
) -> IQLAggregationQuery:
    """
    Parses the response from the LLM to IQL.

    Args:
        response: LLM response.
        allowed_functions: List of functions that can be used in the IQL.
        event_tracker: Event tracker to be used for auditing.

    Returns:
        IQL query for aggregations.

    Raises:
        UnsuppotedQueryError: When IQL generator is unable to construct a query with given aggregations.
    """
    if "unsupported query" in response.lower():
        raise UnsupportedQueryError

    return await IQLAggregationQuery.parse(
        source=response,
        allowed_functions=allowed_functions,
        event_tracker=event_tracker,
    )


def _decision_parser(response: str) -> bool:
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
            methods: List of methods exposed by the view.
            examples: List of examples to be injected into the conversation.
            aggregations: List of aggregations exposed by the view.
        """
        super().__init__(examples)
        self.question = question
        self.methods = "\n".join(str(method) for method in methods)


FILTERING_DECISION_TEMPLATE = PromptTemplate[DecisionPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "Given a question, determine whether the answer requires data filtering in order to compute it.\n"
                "Data filtering is a process in which the result set is filtered based on the specific features "
                "stated in the question. Such a question can be easily identified by using words that refer to "
                "specific feature values (rather than feature names).\n"
                "Look for words indicating specific values that the answer should contain. \n\n"
                "---\n\n"
                "Follow the following format.\n\n"
                "Question: ${{question}}\n"
                "Reasoning: Let's think step by step in order to ${{produce the decision}}. We...\n"
                "Decision: indicates whether the answer to the question requires data filtering. "
                "(Respond with True or False)\n\n"
            ),
        },
        {
            "role": "user",
            "content": ("Question: {question}\n" "Reasoning: Let's think step by step in order to "),
        },
    ],
    response_parser=_decision_parser,
)

AGGREGATION_DECISION_TEMPLATE = PromptTemplate[DecisionPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "Given a question, determine whether the answer requires data aggregation in order to compute it.\n"
                "Data aggregation is a process in which we calculate a single values for a group of rows in the "
                "result set.\n"
                "Most common aggregation functions are counting, averaging, summing, but other types of aggregation "
                "are possible.\n\n"
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
            "content": "Question: {question}\n" "Reasoning: Let's think step by step in order to ",
        },
    ],
    response_parser=_decision_parser,
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
    response_parser=_iql_filters_parser,
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
    response_parser=_iql_aggregation_parser,
)
