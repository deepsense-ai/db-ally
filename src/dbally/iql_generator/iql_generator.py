from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.iql_prompt_template import IQL_GENERATION_TEMPLATE, IQLPromptFormat
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompt import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


class IQLGenerator:
    """
    Class used to generate IQL from natural language question.

    In db-ally, LLM uses IQL (Intermediate Query Language) to express complex queries in a simplified way.
    The class used to generate IQL from natural language query is `IQLGenerator`.

    IQL generation is done using the method `self.generate_iql`.
    It uses LLM to generate text-based responses, passing in the prompt template, formatted filters, and user question.
    """

    def __init__(self, llm: LLM, prompt_template: Optional[PromptTemplate[IQLPromptFormat]] = None) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            llm: LLM used to generate IQL
        """
        self._llm = llm
        self._prompt_template = prompt_template or IQL_GENERATION_TEMPLATE

    async def generate_iql(
        self,
        question: str,
        filters: List[ExposedFunction],
        event_tracker: EventTracker,
        examples: Optional[List[ExposedFunction]] = None,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> IQLQuery:
        """
        Generates IQL in text form using LLM.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            event_tracker: Event store used to audit the generation process.
            examples: List of examples to be injected into the conversation.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors.

        Returns:
            Generated IQL query.
        """
        prompt_format = IQLPromptFormat(
            question=question,
            filters=filters,
            examples=examples,
        )
        formatted_prompt = self._prompt_template.format_prompt(prompt_format)

        for _ in range(n_retries + 1):
            response = await self._llm.generate_text(
                prompt=formatted_prompt,
                event_tracker=event_tracker,
                options=llm_options,
            )
            formatted_prompt = formatted_prompt.add_assistant_message(response)
            try:
                iql = formatted_prompt.response_parser(response)
                # TODO: Move IQL query parsing to prompt response parser
                return await IQLQuery.parse(
                    source=iql,
                    allowed_functions=filters,
                    event_tracker=event_tracker,
                )
            except IQLError as e:
                formatted_prompt = formatted_prompt.add_user_message(
                    f"Unfortunately, generated IQL is not valid. Please try again, \
                    generation of correct IQL is very important. Below you have errors generated by the system:\n {e}"
                )
