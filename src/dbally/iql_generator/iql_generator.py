import asyncio
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar, Union, Type

from dbally.audit.event_tracker import EventTracker
from dbally.iql import IQLError, IQLQuery
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.iql_generator.prompt import (
    FilteringDecisionPrompt, DecisionPromptInput, IQLGenerationPromptInput,
    UnsupportedQueryError, FiltersGenerationPrompt, AggregationDecisionPrompt, AggregationsGenerationPrompt
)
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction

from ragbits.core.llms import LLM
from ragbits.core.options import Options
from ragbits.core.prompt import Prompt

IQLQueryT = TypeVar("IQLQueryT", bound=IQLQuery)


@dataclass
class IQLGeneratorState:
    """
    State of the IQL generator.
    """

    filters: Optional[Union[IQLFiltersQuery, Exception]] = None
    aggregation: Optional[Union[IQLAggregationQuery, Exception]] = None

    @property
    def failed(self) -> bool:
        """
        Checks if the generation failed.

        Returns:
            True if the generation failed, False otherwise.
        """
        return isinstance(self.filters, Exception) or isinstance(self.aggregation, Exception)


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
            FilteringDecisionPrompt,
            FiltersGenerationPrompt,
        )
        self._aggregation_generation = aggregation_generation or IQLOperationGenerator[IQLAggregationQuery](
            AggregationDecisionPrompt,
            AggregationsGenerationPrompt,
        )

    # pylint: disable=too-many-arguments
    async def __call__(
        self,
        *,
        question: str,
        filters: List[ExposedFunction],
        aggregations: List[ExposedFunction],
        examples: List[FewShotExample],
        llm: LLM,
        llm_options: Optional[Options] = None,
        n_retries: int = 3,
    ) -> IQLGeneratorState:
        """
        Generates IQL operations for the given question.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
            aggregations: List of aggregations exposed by the view.
            examples: List of examples to be injected during filters and aggregation generation.
            llm: LLM used to generate IQL.
            event_tracker: Event store used to audit the generation process.
            llm_options: Options to use for the LLM client.
            n_retries: Number of retries to regenerate IQL in case of errors in parsing or LLM connection.

        Returns:
            Generated IQL operations.
        """
        filters, aggregation = await asyncio.gather(
            self._filters_generation(
                question=question,
                methods=filters,
                examples=examples,
                llm=llm,
                llm_options=llm_options,
                n_retries=n_retries,
            ),
            self._aggregation_generation(
                question=question,
                methods=aggregations,
                examples=examples,
                llm=llm,
                llm_options=llm_options,
                n_retries=n_retries,
            ),
            return_exceptions=True,
        )
        return IQLGeneratorState(
            filters=filters,
            aggregation=aggregation,
        )


class IQLOperationGenerator(Generic[IQLQueryT]):
    """
    Generates IQL queries for the given question.
    """

    def __init__(
        self,
        assessor_prompt: Type[Prompt],
        generator_prompt: Type[Prompt],
    ) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            assessor_prompt: Prompt template for filtering decision making.
            generator_prompt: Prompt template for IQL generation.
        """
        self.assessor = IQLQuestionAssessor(assessor_prompt)
        self.generator = IQLQueryGenerator[IQLQueryT](generator_prompt)

    async def __call__(
        self,
        *,
        question: str,
        methods: List[ExposedFunction],
        examples: List[FewShotExample],
        llm: LLM,
        llm_options: Optional[Options] = None,
        n_retries: int = 3,
    ) -> Optional[IQLQueryT]:
        """
        Generates IQL query for the given question.

        Args:
            llm: LLM used to generate IQL.
            question: User question.
            methods: List of methods exposed by the view.
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
            n_retries=n_retries,
        )
        if not decision:
            return None

        return await self.generator(
            question=question,
            methods=methods,
            examples=examples,
            llm=llm,
            llm_options=llm_options,
            n_retries=n_retries,
        )


class IQLQuestionAssessor:
    """
    Assesses whether a question requires applying IQL operation or not.
    """

    def __init__(self, prompt: Type[Prompt]) -> None:
        self.prompt = prompt

    async def __call__(
        self,
        *,
        question: str,
        llm: LLM,
        llm_options: Optional[Options] = None,
        n_retries: int = 3,
    ) -> bool:
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
        formatted_prompt = self.prompt(DecisionPromptInput(question=question))

        for retry in range(n_retries + 1):
            try:
                response = await llm.generate(
                    prompt=formatted_prompt,
                    options=llm_options,
                )
                return response
            except Exception as exc:  # TODO: LLMError is not defined
                if retry == n_retries:
                    raise exc


class IQLQueryGenerator(Generic[IQLQueryT]):
    """
    Generates IQL queries for the given question.
    """

    ERROR_MESSAGE = "Unfortunately, generated IQL is not valid. Please try again, \
        generation of correct IQL is very important. Below you have errors generated by the system:\n{error}"

    def __init__(self, prompt: Type[Prompt]) -> None:
        self.prompt = prompt

    async def __call__(
        self,
        *,
        question: str,
        methods: List[ExposedFunction],
        examples: List[FewShotExample],
        llm: LLM,
        llm_options: Optional[Options] = None,
        event_tracker: Optional[EventTracker] = None,
        n_retries: int = 3,
    ) -> IQLQueryT:
        """
        Generates IQL query for the given question.

        Args:
            question: User question.
            filters: List of filters exposed by the view.
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
        formatted_prompt = self.prompt(IQLGenerationPromptInput(
            question=question,
            methods=[str(x) for x in methods],
            # examples=examples,
        ))

        for retry in range(n_retries + 1):
            try:
                response = await llm.generate(
                    prompt=formatted_prompt,
                    options=llm_options,
                )
                if "unsupported query" in response.lower():
                    raise UnsupportedQueryError

                return await IQLFiltersQuery.parse(
                    source=response,
                    allowed_functions=methods,
                    event_tracker=event_tracker,
                )
            except Exception as exc:  # TODO: LLMError is not defined
                if retry == n_retries:
                    raise exc
            except IQLError as exc:
                if retry == n_retries:
                    raise exc
                formatted_prompt = formatted_prompt.add_assistant_message(response)
                formatted_prompt = formatted_prompt.add_user_message(self.ERROR_MESSAGE.format(error=exc))
