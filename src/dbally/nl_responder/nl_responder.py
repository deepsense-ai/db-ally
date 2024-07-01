from typing import Optional

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.nl_responder.nl_responder_prompt_template import NLResponderPromptFormat, default_nl_responder_template
from dbally.nl_responder.query_explainer_prompt_template import (
    QueryExplainerPromptFormat,
    default_query_explainer_template,
)
from dbally.prompts.template import PromptTemplate


class NLResponder:
    """
    Class used to generate natural language response from the database output.
    """

    def __init__(
        self,
        llm: LLM,
        prompt_template: Optional[PromptTemplate[NLResponderPromptFormat]] = None,
        explainer_prompt_template: Optional[PromptTemplate[QueryExplainerPromptFormat]] = None,
        max_tokens_count: int = 4096,
    ) -> None:
        """
        Constructs a new NLResponder instance.

        Args:
            llm: LLM used to generate natural language response.
            prompt_template: Template for the prompt used to generate the NL response
                if not set defaults to `nl_responder_prompt_template`.
             explainer_prompt_template: Template for the prompt used to generate the iql explanation
                if not set defaults to `default_query_explainer_template`.
            max_tokens_count: Maximum number of tokens that can be used in the prompt.
        """
        self._llm = llm
        self._prompt_template = prompt_template or default_nl_responder_template
        self._explainer_prompt_template = explainer_prompt_template or default_query_explainer_template
        self._max_tokens_count = max_tokens_count

    async def generate_response(
        self,
        result: ViewExecutionResult,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
    ) -> str:
        """
        Uses LLM to generate a response in natural language form.

        Args:
            result: Object representing the result of the query execution.
            question: User question.
            event_tracker: Event store used to audit the generation process.
            llm_options: Options to use for the LLM client.

        Returns:
            Natural language response to the user question.
        """
        prompt_format = NLResponderPromptFormat(
            question=question,
            results=result.results,
        )
        formatted_prompt = self._prompt_template.format_prompt(prompt_format)
        tokens_count = self._llm.count_tokens(formatted_prompt)

        if tokens_count > self._max_tokens_count:
            prompt_format = QueryExplainerPromptFormat(
                question=question,
                context=result.context,
                results=result.results,
            )
            formatted_prompt = self._explainer_prompt_template.format_prompt(prompt_format)
            llm_response = await self._llm.generate_text(
                prompt=formatted_prompt,
                event_tracker=event_tracker,
                options=llm_options,
            )
            return llm_response

        llm_response = await self._llm.generate_text(
            prompt=formatted_prompt,
            event_tracker=event_tracker,
            options=llm_options,
        )
        return llm_response
