from typing import List, Optional, Tuple

from dbally.audit.event_tracker import EventTracker
from dbally.iql_generator.iql_prompt_template import IQL_GENERATION_TEMPLATE
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompts import PromptTemplate
from dbally.prompts.formatters import IQLInputFormatter
from dbally.views.exposed_functions import ExposedFunction


class IQLGenerator:
    """
    Class used to generate IQL from natural language question.

    In db-ally, LLM uses IQL (Intermediate Query Language) to express complex queries in a simplified way.
    The class used to generate IQL from natural language query is `IQLGenerator`.

    IQL generation is done using the method `self.generate_iql`.
    It uses LLM to generate text-based responses, passing in the prompt template, formatted filters, and user question.
    """

    def __init__(self, llm: LLM, prompt_template: Optional[PromptTemplate] = None) -> None:
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
        prompt_template: Optional[PromptTemplate] = None,
        llm_options: Optional[LLMOptions] = None,
    ) -> Tuple[str, PromptTemplate]:
        """
        Generates IQL in text form using LLM.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            event_tracker: Event store used to audit the generation process.
            examples: List of examples to be injected into the conversation.
            prompt_template: Prompt template with error messages.
            llm_options: Options to use for the LLM client.

        Returns:
            Tuple containing IQL and formatted prompt template.
        """
        formatter = IQLInputFormatter(
            question=question,
            filters=filters,
            examples=examples,
        )
        formatted_prompt = formatter(prompt_template or self._prompt_template)

        llm_response = await self._llm.generate_text(
            prompt=formatted_prompt,
            event_tracker=event_tracker,
            options=llm_options,
        )
        formatted_prompt = formatted_prompt.add_assistant_message(llm_response)
        iql = formatted_prompt.response_parser(llm_response)

        return iql, formatted_prompt
