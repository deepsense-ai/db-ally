from typing import List, Optional

from dbally.audit import EventTracker
from dbally.exceptions import UnsupportedAggregationError

from dbally.iql import IQLQuery
from dbally.llms.base import LLM
from dbally.llms.clients import LLMOptions
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


class AggregationFormatter:
    def __init__(self, llm: LLM, prompt_template: Optional[PromptTemplate[AggregationPromptFormat]] = None) -> None:
        """
        Constructs a new AggregationFormatter instance.

        Args:
            llm: LLM used to generate IQL
            prompt_template: If not provided by the users is set to `AGGREGATION_GENERATION_TEMPLATE`
        """
        self._llm = llm
        self._prompt_template = prompt_template or AGGREGATION_GENERATION_TEMPLATE

    async def format_to_query_object(
        self,
        question: str,
        event_tracker: EventTracker,
        aggregations: List[ExposedFunction] = None,
        llm_options: Optional[LLMOptions] = None,
    ) -> IQLQuery:

        prompt_format = AggregationPromptFormat(
            question=question,
            aggregations=aggregations,
        )

        formatted_prompt = self._prompt_template.format_prompt(prompt_format)

        response = await self._llm.generate_text(
            prompt=formatted_prompt,
            event_tracker=event_tracker,
            options=llm_options,
        )
        # TODO: Move response parsing to llm generate_text method
        agg = formatted_prompt.response_parser(response)
        # TODO: Move IQL query parsing to prompt response parser
        return await IQLQuery.parse(
            source=agg,
            allowed_functions=aggregations or [],
            event_tracker=event_tracker,
        )


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
        {
            "role": "user",
            "content": "{question}"
        },
    ],
    response_parser=_validate_agg_response,
)
