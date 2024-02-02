import copy
from typing import Callable, Dict, Optional, Union

from dbally.data_models.prompts import ChatFormat, IQLPromptTemplate, default_view_selector_template
from dbally.iql_generator.iql_generator import BaseLLMClient
from dbally.prompts import PromptBuilder
from dbally.view_selection.base import ViewSelector


class DefaultViewSelector(ViewSelector):
    """
    ViewSelector utilises the LLM model to select the best view to answer the user question.

    Attributes:
        llm_client: LLM client used to generate IQL
        prompt_template: template for the prompt
        prompt_builder: PromptBuilder used to insert arguments into the prompt and adjust style per model
        promptify_view: Function formatting filters and actions for prompt
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,  # temporary
        prompt_template: Optional[IQLPromptTemplate] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        promptify_views: Optional[Callable] = None,
    ) -> None:
        self._llm_client = llm_client
        self._prompt_template = prompt_template or copy.deepcopy(default_view_selector_template)
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._promptify_views = promptify_views or _promptify_views
        self.last_prompt: Union[str, ChatFormat, None] = None  # todo: drop it when we have auditing

    async def select_view(self, question: str, views: Dict[str, str]) -> str:
        """
        Based on user question and list of available views select most relevant one.

        Args:
            question: user question.
            views: dictionary of available view names with corresponding descriptions.

        Returns:
            most relevant view name.
        """

        views_for_prompt = self._promptify_views(views)

        _prompt = self._prompt_builder.build(
            self._prompt_template,
            fmt={"views": views_for_prompt, "question": question},
        )
        self.last_prompt = _prompt
        llm_response = self._llm_client.generate(_prompt, self._prompt_template.response_format)
        selected_view = self._prompt_template.llm_response_parser(llm_response)
        return selected_view


def _promptify_views(views: Dict[str, str]) -> str:
    """
    Formats views for prompt

    Args:

    Returns:
        views_for_prompt: views formatted for prompt
    """

    return "\n".join([f"{name}: {description}" for name, description in views.items()])
