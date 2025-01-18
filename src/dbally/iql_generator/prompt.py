# pylint: disable=C0301

from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.exceptions import DbAllyError
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.views.exposed_functions import ExposedFunction

from pydantic import BaseModel
from ragbits.core.prompt import Prompt

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



class IQLGenerationPromptInput(BaseModel):
    question: str
    methods: List[str]


class DecisionPromptInput(BaseModel):
    """
    Input for the filtering decision prompt.
    """

    question: str


class FilteringDecisionPrompt(Prompt[DecisionPromptInput, bool]):
    system_prompt = """
        Given a question, determine whether the answer requires data filtering in order to compute it.
        Data filtering is a process in which the result set is filtered based on the specific features
        stated in the question. Such a question can be easily identified by using words that refer to
        specific feature values (rather than feature names).

        Look for words indicating specific values that the answer should contain.

        ---

        Follow the following format.

        Question: $\{\{question\}\}
        Reasoning: Let's think step by step in order to $\{\{produce the decision\}\}. We...
        Decision: indicates whether the answer to the question requires data filtering.
        (Respond with True or False)"
    """

    user_prompt = "Question: {{question}}\nReasoning: Let's think step by step in order to "
    response_parser = _decision_parser


class AggregationDecisionPrompt(Prompt[DecisionPromptInput, bool]):
    system_prompt = """
        Given a question, determine whether the answer requires data aggregation in order to compute it.
        Data aggregation is a process in which we calculate a single value for a group of rows in the result set.
        Most common aggregation functions are counting, averaging, summing, but other types of aggregation are possible.

        ---

        Follow the following format.

        Question: $\{\{question\}\}
        Reasoning: Let's think step by step in order to $\{\{produce the decision\}\}. We...
        Decision: indicates whether the answer to the question requires data filtering.
        (Respond with True or False)"
    """

    user_prompt = "Question: {{question}}\nReasoning: Let's think step by step in order to "
    response_parser = _decision_parser

class FiltersGenerationPrompt(Prompt[IQLGenerationPromptInput, str]):
    system_prompt = """
        You have access to an API that lets you query a database:
        {% for method in methods %}
        {{ method }}
        {% endfor %}
        Suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).
        Remember! Don't give any comments, just the function calls.
        The output will look like this:
        filter1("arg1") AND (NOT filter2(120) OR filter3(True))
        DO NOT INCLUDE arguments names in your response. Only the values.
        You MUST use only these methods:
        {% for method in methods %}
        {{ method }}
        {% endfor %}
        It is VERY IMPORTANT not to use methods other than those listed above.
        If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`
        This is CRUCIAL, otherwise the system will crash.
    """

    user_prompt = "{{ question }}"


class AggregationsGenerationPrompt(Prompt[IQLGenerationPromptInput, str]):
    system_prompt = """
        You have access to an API that lets you query a database supporting a SINGLE aggregation.
        When prompted for an aggregation, use the following methods:
        {% for method in methods %}
        {{ method }}
        {% endfor %}
        DO NOT INCLUDE arguments names in your response. Only the values.
        You MUST use only these methods:
        {% for method in methods %}
        {{ method }}
        {% endfor %}
        It is VERY IMPORTANT not to use methods other than those listed above.
        If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`
        This is CRUCIAL to put `UNSUPPORTED QUERY` text only, otherwise the system will crash.
        Structure output to resemble the following pattern:
        aggregation1("arg1", arg2)
    """

    user_prompt = "{{ question }}"