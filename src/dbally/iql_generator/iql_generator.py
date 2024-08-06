from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.prompt import (
    FILTERING_DECISION_TEMPLATE,
    IQL_GENERATION_TEMPLATE,
    FilteringDecisionPromptFormat,
    IQLGenerationPromptFormat,
)
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.llms.clients.exceptions import LLMError
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

    def __init__(
        self,
        llm: LLM,
        *,
        decision_prompt: Optional[PromptTemplate[FilteringDecisionPromptFormat]] = None,
        generation_prompt: Optional[PromptTemplate[IQLGenerationPromptFormat]] = None,
    ) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            llm: LLM used to generate IQL.
            decision_prompt: Prompt template for filtering decision making.
            generation_prompt: Prompt template for IQL generation.
        """
        self._llm = llm
        self._decision_prompt = decision_prompt or FILTERING_DECISION_TEMPLATE
        self._generation_prompt = generation_prompt or IQL_GENERATION_TEMPLATE

    async def generate(
        self,
        question: str,
        filters: List[ExposedFunction],
        event_tracker: EventTracker,
        examples: Optional[List[FewShotExample]] = None,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> Optional[IQLQuery]:
        """
        Generates IQL in text form using LLM.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            event_tracker: Event store used to audit the generation process.
            examples: List of examples to be injected into the conversation.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors in parsing or LLM connection.

        Returns:
            Generated IQL query or None if the decision is not to continue.

        Raises:
            LLMError: If LLM text generation fails after all retries.
            IQLError: If IQL parsing fails after all retries.
            UnsupportedQueryError: If the question is not supported by the view.
        """
        decision = await self._decide_on_generation(
            question=question,
            event_tracker=event_tracker,
            llm_options=llm_options,
            n_retries=n_retries,
        )
        if not decision:
            return None

        return await self._generate_iql(
            question=question,
            filters=filters,
            event_tracker=event_tracker,
            examples=examples,
            llm_options=llm_options,
            n_retries=n_retries,
        )

    async def _decide_on_generation(
        self,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> bool:
        """
        Decides whether the question requires filtering or not.

        Args:
            question: User question.
            event_tracker: Event store used to audit the generation process.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to LLM API in case of errors.

        Returns:
            Decision whether to generate IQL or not.

        Raises:
            LLMError: If LLM text generation fails after all retries.
        """
        prompt_format = FilteringDecisionPromptFormat(question=question)
        formatted_prompt = self._decision_prompt.format_prompt(prompt_format)

        for retry in range(n_retries + 1):
            try:
                response = await self._llm.generate_text(
                    prompt=formatted_prompt,
                    event_tracker=event_tracker,
                    options=llm_options,
                )
                # TODO: Move response parsing to llm generate_text method
                return formatted_prompt.response_parser(response)
            except LLMError as exc:
                if retry == n_retries:
                    raise exc

    async def _generate_iql(
        self,
        question: str,
        filters: List[ExposedFunction],
        event_tracker: EventTracker,
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
            examples: List of examples to be injected into the conversation.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors in parsing or LLM connection.

        Returns:
            Generated IQL query.

        Raises:
            LLMError: If LLM text generation fails after all retries.
            IQLError: If IQL parsing fails after all retries.
            UnsupportedQueryError: If the question is not supported by the view.
        """
        prompt_format = IQLGenerationPromptFormat(
            question=question,
            filters=filters,
            examples=examples,
        )
        formatted_prompt = self._generation_prompt.format_prompt(prompt_format)

        for retry in range(n_retries + 1):
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
                    allowed_functions=filters,
                    event_tracker=event_tracker,
                )
            except LLMError as exc:
                if retry == n_retries:
                    raise exc
            except IQLError as exc:
                if retry == n_retries:
                    raise exc
                formatted_prompt = formatted_prompt.add_assistant_message(response)
                formatted_prompt = formatted_prompt.add_user_message(ERROR_MESSAGE.format(error=exc))
