import copy
from typing import Callable, List, Optional, Tuple, Union

from dbally.audit.event_store import EventStore
from dbally.data_models.prompts.iql_prompt_template import IQLPromptTemplate, default_iql_template
from dbally.data_models.prompts.prompt_template import ChatFormat
from dbally.llm_client.base import LLMClient
from dbally.prompts.prompt_builder import PromptBuilder
from dbally.views.base import ExposedFunction


class IQLGenerator:
    """
    Class used to generate IQL from natural language question.

    Attributes:
        llm_client: LLM client used to generate IQL
        prompt_template: template for the prompt
        prompt_builder: PromptBuilder used to insert arguments into the prompt and adjust style per model
        promptify_view: Function formatting filters and actions for prompt
    """

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_template: Optional[IQLPromptTemplate] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        promptify_view: Optional[Callable] = None,
    ) -> None:
        self._llm_client = llm_client
        self._prompt_template = prompt_template or copy.deepcopy(default_iql_template)
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._promptify_view = promptify_view or _promptify_filters_and_actions
        self.last_prompt: Union[str, ChatFormat, None] = None  # todo: drop it when we have auditing

    async def generate_iql(
        self, filters: List[ExposedFunction], actions: List[ExposedFunction], question: str,
        event_store: EventStore
    ) -> Tuple[str, str]:
        # todo: add more generation-related arguments here once BaseLLM interface is established
        """Uses LLM to generate IQL in text form

        Args:
            question: user question
            filters: list of filters exposed by the view
            actions: list of actions exposed by the view

        Returns:
            IQL - iql generated based on the user question
        """
        filters_for_prompt, actions_for_prompt = self._promptify_view(filters, actions)

        _prompt = self._prompt_builder.build(
            self._prompt_template,
            fmt={"filters": filters_for_prompt, "actions": actions_for_prompt, "question": question},
        )
        llm_response = await self._llm_client.text_generation(
            template=self._prompt_template,
            fmt={"filters": filters_for_prompt, "actions": actions_for_prompt, "question": question},
            event_store=event_store
        )
        iql_filters, iql_actions = self._prompt_template.llm_response_parser(llm_response)
        self.last_prompt = _prompt
        return iql_filters, iql_actions


# todo: after default __repr__ for filters/actions is implemented, replace this body with str()
def _promptify_filters_and_actions(filters: List[ExposedFunction], actions: List[ExposedFunction]) -> Tuple[str, str]:
    """
    Formats filters/actions for prompt

    Args:
        filters: list of filters exposed by the view
        actions: list of actions exposed by the view

    Returns:
        filters_for_prompt: filters formatted for prompt
        actions_for_prompt: actions formatted for prompt
    """
    filters_for_prompt = "\n".join(
        [
            filter.name + "(" + param.name + ": " + str(param.type.__name__) + ")"
            for filter in filters
            for param in filter.parameters
        ]
    )
    actions_for_prompt = "\n".join([action.name + "()" for action in actions])
    return filters_for_prompt, actions_for_prompt
