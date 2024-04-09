import copy
from typing import Callable, List, Optional, Tuple, TypeVar

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.prompts.iql_prompt_template import IQLPromptTemplate, default_iql_template
from dbally.llm_client.base import LLMClient
from dbally.prompts.prompt_builder import PromptBuilder
from dbally.views.base import ExposedFunction


class IQLGenerator:
    """
    Class used to generate IQL from natural language question.

    In db-ally, LLM uses IQL (Intermediate Query Language) to express complex queries in a simplified way.
    The class used to generate IQL from natural language query is `IQLGenerator`.

    IQL generation is done using the method `self.generate_iql`.
    It uses LLM to generate text-based responses, passing in the prompt template, formatted filters, and user question.
    """

    _ERROR_MSG_PREFIX = "Unfortunately, generated IQL is not valid. Please try again, \
                        generation of correct IQL is very important. Below you have errors generated by the system: \n"

    TException = TypeVar("TException", bound=Exception)

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_template: Optional[IQLPromptTemplate] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        promptify_view: Optional[Callable] = None,
    ) -> None:
        """
        Args:
            llm_client: LLM client used to generate IQL
            prompt_template: If not provided by the users is set to `default_iql_template`
            prompt_builder: PromptBuilder used to insert arguments into the prompt and adjust style per model.
            promptify_view: Function formatting filters for prompt
        """
        self._llm_client = llm_client
        self._prompt_template = prompt_template or copy.deepcopy(default_iql_template)
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._promptify_view = promptify_view or _promptify_filters

    async def generate_iql(
        self,
        filters: List[ExposedFunction],
        question: str,
        event_tracker: EventTracker,
        conversation: Optional[IQLPromptTemplate] = None,
    ) -> Tuple[str, IQLPromptTemplate]:
        """
        Uses LLM to generate IQL in text form

        Args:
            question: user question
            filters: list of filters exposed by the view
            event_tracker: event store used to audit the generation process
            conversation: conversation to be continued

        Returns:
            IQL - iql generated based on the user question
        """
        filters_for_prompt = self._promptify_view(filters)

        template = conversation or self._prompt_template

        llm_response = await self._llm_client.text_generation(
            template=template,
            fmt={"filters": filters_for_prompt, "question": question},
            event_tracker=event_tracker,
        )

        iql_filters = self._prompt_template.llm_response_parser(llm_response)

        if conversation is None:
            conversation = self._prompt_template

        conversation = conversation.add_assistant_message(content=llm_response)

        return iql_filters, conversation

    def add_error_msg(self, conversation: IQLPromptTemplate, errors: List[TException]) -> IQLPromptTemplate:
        """
        Appends error message returned due to the invalid IQL generated to the conversation

        Args:
            conversation (IQLPromptTemplate): conversation containing current IQL generation trace
            errors (List[Exception]): errors to be appended

        Returns:
            IQLPromptTemplate: Conversation extended with errors
        """

        msg = self._ERROR_MSG_PREFIX
        for error in errors:
            msg += str(error) + "\n"

        return conversation.add_user_message(content=msg)


def _promptify_filters(
    filters: List[ExposedFunction],
) -> str:
    """
    Formats filters for prompt

    Args:
        filters: list of filters exposed by the view

    Returns:
        filters_for_prompt: filters formatted for prompt
    """
    filters_for_prompt = "\n".join([str(filter) for filter in filters])
    return filters_for_prompt
