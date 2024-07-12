from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.prompt import (
    IQL_GENERATION_TEMPLATE,
    IQL_GENERATION_TEMPLATE_AGGREGATION,
    IQLGenerationPromptFormat,
)
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction

ERROR_MESSAGE = "Unfortunately, generated IQL is not valid. Please try again, \
    generation of correct IQL is very important. Below you have errors generated by the system:\n{error}"


class IQLGenerator:
    """
    Class used to generate IQL from natural language question.

    In db-ally, LLM uses IQL (Intermediate Query Language) to express complex queries in a simplified way.
    The class used to generate IQL from natural language query is `IQLGenerator`.

    IQL generation is done using the method `self.generate_iql`.
    It uses LLM to generate text-based responses, passing in the prompt template, formatted filters, and user question.
    """

    def __init__(self, llm: LLM, prompt_template: Optional[PromptTemplate[IQLGenerationPromptFormat]] = None) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            llm: LLM used to generate IQL
            prompt_template: If not provided by the users is set to `default_iql_template`
        """
        self._llm = llm
        self._prompt_template = prompt_template or IQL_GENERATION_TEMPLATE

    async def generate_iql(
        self,
        question: str,
        filters: List[ExposedFunction],
        event_tracker: EventTracker,
        aggregations: List[ExposedFunction] = None,
        examples: Optional[List[FewShotExample]] = None,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> IQLQuery:
        """
        Generates IQL in text form using LLM.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            event_tracker: Event store used to audit the generation process.
            aggregations: List of aggregations to be applied on the view.
            examples: List of examples to be injected into the conversation.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors.

        Returns:
            Generated IQL query.
        """
        prompt_format = IQLGenerationPromptFormat(
            question=question,
            filters=filters,
            aggregations=aggregations,
            examples=examples,
        )
        if aggregations and not filters:
            self._prompt_template = IQL_GENERATION_TEMPLATE_AGGREGATION

        formatted_prompt = self._prompt_template.format_prompt(prompt_format)

        for _ in range(n_retries + 1):
            try:
                response = await self._llm.generate_text(
                    prompt=formatted_prompt,
                    event_tracker=event_tracker,
                    options=llm_options,
                )
                # TODO: Move response parsing to llm generate_text method
                iql = formatted_prompt.response_parser(response)
                # TODO: Move IQL query parsing to prompt response parser
                return await IQLQuery.parse(
                    source=iql,
                    allowed_functions=filters or [] + aggregations or [],
                    event_tracker=event_tracker,
                )
            except IQLError as exc:
                formatted_prompt = formatted_prompt.add_assistant_message(response)
                formatted_prompt = formatted_prompt.add_user_message(ERROR_MESSAGE.format(error=exc))
