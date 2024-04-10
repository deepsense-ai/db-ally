import copy
from typing import Callable, Dict, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.prompts import IQLPromptTemplate, default_view_selector_template
from dbally.llm_client.base import LLMClient
from dbally.prompts import PromptBuilder
from dbally.view_selection.base import ViewSelector


class LLMViewSelector(ViewSelector):
    """
    The `LLMViewSelector` utilises LLMs to select the most suitable view to answer the user question.

    Its primary function is to determine the optimal view that can effectively be used to answer a user's question.

    The method used to select the most relevant view is `self.select_view`.
    It formats views using view.name: view.description format and then calls LLM Client,
    ultimately returning the name of the most suitable view.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_template: Optional[IQLPromptTemplate] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        promptify_views: Optional[Callable[[Dict[str, str]], str]] = None,
    ) -> None:
        """
        Args:
            llm_client: LLM client used to generate IQL
            prompt_template: template for the prompt used for the view selection
            prompt_builder: PromptBuilder used to insert arguments into the prompt and adjust style per model
            promptify_views: Function formatting filters for prompt. By default names and descriptions of\
            all views are concatenated
        """
        self._llm_client = llm_client
        self._prompt_template = prompt_template or copy.deepcopy(default_view_selector_template)
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._promptify_views = promptify_views or _promptify_views

    async def select_view(self, question: str, views: Dict[str, str], event_tracker: EventTracker) -> str:
        """
        Based on user question and list of available views select the most relevant one by prompting LLM.

        Args:
            question: user question asked in the natural language e.g "Do we have any data scientists?"
            views: dictionary of available view names with corresponding descriptions.
            event_tracker: event tracker used to audit the selection process.

        Returns:
            The most relevant view name.
        """

        views_for_prompt = self._promptify_views(views)

        llm_response = await self._llm_client.text_generation(
            self._prompt_template, fmt={"views": views_for_prompt, "question": question}, event_tracker=event_tracker
        )
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
