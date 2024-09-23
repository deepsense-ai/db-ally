import asyncio
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar, Union

from dbally.audit.event_tracker import EventTracker
from dbally.context.context import BaseCallerContext
from dbally.iql import IQLError, IQLQuery
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.iql_generator.prompt import (
    AGGREGATION_DECISION_TEMPLATE,
    AGGREGATION_GENERATION_TEMPLATE,
    FILTERING_DECISION_TEMPLATE,
    FILTERS_GENERATION_TEMPLATE,
    DecisionPromptFormat,
    IQLGenerationPromptFormat,
)
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.llms.clients.exceptions import LLMError
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction

IQLQueryT = TypeVar("IQLQueryT", bound=IQLQuery)


@dataclass
class IQLGeneratorState:
    """
    State of the IQL generator.
    """

    filters: Optional[Union[IQLFiltersQuery, BaseException]] = None
    aggregation: Optional[Union[IQLAggregationQuery, BaseException]] = None


class IQLGenerator:
    """
    Orchestrates all IQL operations for the given question.
    """

    def __init__(
        self,
        filters_generation: Optional["IQLOperationGenerator"] = None,
        aggregation_generation: Optional["IQLOperationGenerator"] = None,
    ) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            decision_prompt: Prompt template for filtering decision making.
            generation_prompt: Prompt template for IQL generation.
        """
        self._filters_generation = filters_generation or IQLOperationGenerator[IQLFiltersQuery](
            FILTERING_DECISION_TEMPLATE,
            FILTERS_GENERATION_TEMPLATE,
        )
        self._aggregation_generation = aggregation_generation or IQLOperationGenerator[IQLAggregationQuery](
            AGGREGATION_DECISION_TEMPLATE,
            AGGREGATION_GENERATION_TEMPLATE,
        )

    # pylint: disable=too-many-arguments
    async def __call__(
        self,
        *,
        question: str,
        filters: List[ExposedFunction],
        aggregations: List[ExposedFunction],
        contexts: List[BaseCallerContext],
        examples: List[FewShotExample],
        llm: LLM,
        event_tracker: Optional[EventTracker] = None,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> IQLGeneratorState:
        """
        Generates IQL operations for the given question.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            aggregations: List of aggregations exposed by the view.
            contexts: List of contexts to be injected after filters and aggregation generation.
            examples: List of examples to be injected during filters and aggregation generation.
            llm: LLM used to generate IQL.
            event_tracker: Event store used to audit the generation process.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors in parsing or LLM connection.

        Returns:
            Generated IQL operations.
        """
        iql_filters, iql_aggregation = await asyncio.gather(
            self._filters_generation(
                question=question,
                methods=filters,
                contexts=contexts,
                examples=examples,
                llm=llm,
                llm_options=llm_options,
                event_tracker=event_tracker,
                n_retries=n_retries,
            ),
            self._aggregation_generation(
                question=question,
                methods=aggregations,
                contexts=contexts,
                examples=examples,
                llm=llm,
                llm_options=llm_options,
                event_tracker=event_tracker,
                n_retries=n_retries,
            ),
            return_exceptions=True,
        )
        return IQLGeneratorState(
            filters=iql_filters,
            aggregation=iql_aggregation,
        )


class IQLOperationGenerator(Generic[IQLQueryT]):
    """
    Generates IQL queries for the given question.
    """

    def __init__(
        self,
        assessor_prompt: PromptTemplate[DecisionPromptFormat],
        generator_prompt: PromptTemplate[IQLGenerationPromptFormat],
    ) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            assessor_prompt: Prompt template for filtering decision making.
            generator_prompt: Prompt template for IQL generation.
        """
        self.assessor = IQLQuestionAssessor(assessor_prompt)
        self.generator = IQLQueryGenerator[IQLQueryT](generator_prompt)

    # pylint: disable=too-many-arguments
    async def __call__(
        self,
        *,
        question: str,
        methods: List[ExposedFunction],
        contexts: List[BaseCallerContext],
        examples: List[FewShotExample],
        llm: LLM,
        event_tracker: Optional[EventTracker] = None,
        llm_options: Optional[LLMOptions] = None,
        n_retries: int = 3,
    ) -> Optional[IQLQueryT]:
        """
        Generates IQL query for the given question.

        Args:
            llm: LLM used to generate IQL.
            question: User question.
            methods: List of methods exposed by the view.
            contexts: List of contexts to be injected as method arguments.
            examples: List of examples to be injected into the conversation.
            event_tracker: Event store used to audit the generation process.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors in parsing or LLM connection.

        Returns:
            Generated IQL query or None if the decision is not to continue.

        Raises:
            LLMError: If LLM text generation fails after all retries.
            IQLError: If IQL parsing fails after all retries.
            UnsupportedQueryError: If the question is not supported by the view.
        """
        decision = await self.assessor(
            question=question,
            llm=llm,
            llm_options=llm_options,
            event_tracker=event_tracker,
            n_retries=n_retries,
        )
        if not decision:
            return None

        return await self.generator(
            question=question,
            methods=methods,
            contexts=contexts,
            examples=examples,
            llm=llm,
            llm_options=llm_options,
            event_tracker=event_tracker,
            n_retries=n_retries,
        )


class IQLQuestionAssessor:
    """
    Assesses whether a question requires applying IQL operation or not.
    """

    def __init__(self, prompt: PromptTemplate[DecisionPromptFormat]) -> None:
        self.prompt = prompt

    async def __call__(
        self,
        *,
        question: str,
        llm: LLM,
        llm_options: Optional[LLMOptions] = None,
        event_tracker: Optional[EventTracker] = None,
        n_retries: int = 3,
    ) -> Optional[bool]:
        """
        Decides whether the question requires generating IQL or not.

        Args:
            question: User question.
            llm: LLM used to generate IQL.
            llm_options: Options to use for the LLM client.
            event_tracker: Event store used to audit the generation process.
            n_retries: Number of retries to LLM API in case of errors.

        Returns:
            Decision whether to generate IQL or not.

        Raises:
            LLMError: If LLM text generation fails after all retries.
        """
        prompt_format = DecisionPromptFormat(
            question=question,
        )
        formatted_prompt = self.prompt.format_prompt(prompt_format)

        for retry in range(n_retries + 1):
            try:
                response = await llm.generate_text(
                    prompt=formatted_prompt,
                    event_tracker=event_tracker,
                    options=llm_options,
                )
                # TODO: Move response parsing to llm generate_text method
                return formatted_prompt.response_parser(response)
            except LLMError as exc:
                if retry == n_retries:
                    raise exc


class IQLQueryGenerator(Generic[IQLQueryT]):
    """
    Generates IQL queries for the given question.
    """

    ERROR_MESSAGE = "Unfortunately, generated IQL is not valid. Please try again, \
        generation of correct IQL is very important. Below you have errors generated by the system:\n{error}"

    def __init__(self, prompt: PromptTemplate[IQLGenerationPromptFormat]) -> None:
        self.prompt = prompt

    # pylint: disable=too-many-arguments
    async def __call__(
        self,
        *,
        question: str,
        methods: List[ExposedFunction],
        contexts: List[BaseCallerContext],
        examples: List[FewShotExample],
        llm: LLM,
        llm_options: Optional[LLMOptions] = None,
        event_tracker: Optional[EventTracker] = None,
        n_retries: int = 3,
    ) -> Optional[IQLQueryT]:
        """
        Generates IQL query for the given question.

        Args:
            question: User question.
            methods: List of methods exposed by the view.
            contexts: List of contexts to be injected as method arguments.
            examples: List of examples to be injected into the conversation.
            llm: LLM used to generate IQL.
            llm_options: Options to use for the LLM client.
            event_tracker: Event store used to audit the generation process.
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
            methods=methods,
            contexts=contexts,
            examples=examples,
        )
        formatted_prompt = self.prompt.format_prompt(prompt_format)

        for retry in range(n_retries + 1):
            try:
                response = await llm.generate_text(
                    prompt=formatted_prompt,
                    event_tracker=event_tracker,
                    options=llm_options,
                )
                # TODO: Move response parsing to llm generate_text method
                return await formatted_prompt.response_parser(
                    response=response,
                    allowed_functions=methods,
                    allowed_contexts=contexts,
                    event_tracker=event_tracker,
                )
            except (IQLError, LLMError) as exc:
                if retry == n_retries:
                    raise exc
                if isinstance(exc, IQLError):
                    formatted_prompt = formatted_prompt.add_assistant_message(response)
                    formatted_prompt = formatted_prompt.add_user_message(self.ERROR_MESSAGE.format(error=exc))
