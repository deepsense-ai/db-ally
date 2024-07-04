from typing import Dict, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompt.template import PromptTemplate
from dbally.view_selection.base import ViewSelector
from dbally.view_selection.prompt import VIEW_SELECTION_TEMPLATE, ViewSelectionPromptFormat


class LLMViewSelector(ViewSelector):
    """
    The `LLMViewSelector` utilises LLMs to select the most suitable view to answer the user question.

    Its primary function is to determine the optimal view that can effectively be used to answer a user's question.

    The method used to select the most relevant view is `self.select_view`.
    It formats views using view.name: view.description format and then calls LLM Client,
    ultimately returning the name of the most suitable view.
    """

    def __init__(self, llm: LLM, prompt_template: Optional[PromptTemplate[ViewSelectionPromptFormat]] = None) -> None:
        """
        Constructs a new LLMViewSelector instance.

        Args:
            llm: LLM used to generate IQL
            prompt_template: template for the prompt used for the view selection
        """
        self._llm = llm
        self._prompt_template = prompt_template or VIEW_SELECTION_TEMPLATE

    async def select_view(
        self,
        question: str,
        views: Dict[str, str],
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
    ) -> str:
        """
        Based on user question and list of available views select the most relevant one by prompting LLM.

        Args:
            question: user question asked in the natural language e.g "Do we have any data scientists?"
            views: dictionary of available view names with corresponding descriptions.
            event_tracker: event tracker used to audit the selection process.
            llm_options: options to use for the LLM client.

        Returns:
            The most relevant view name.
        """
        prompt_format = ViewSelectionPromptFormat(question=question, views=views)
        formatted_prompt = self._prompt_template.format_prompt(prompt_format)

        llm_response = await self._llm.generate_text(
            prompt=formatted_prompt,
            event_tracker=event_tracker,
            options=llm_options,
        )
        selected_view = self._prompt_template.response_parser(llm_response)
        return selected_view
