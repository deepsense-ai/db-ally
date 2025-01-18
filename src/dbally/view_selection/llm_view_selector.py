from typing import Dict, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.prompt.template import PromptTemplate
from dbally.view_selection.base import ViewSelector
from dbally.view_selection.prompt import ViewSelectionPrompt, ViewSelectionPromptInput

from ragbits.core.llms import LLM
from ragbits.core.prompt import Prompt
from ragbits.core.options import Options

class LLMViewSelector(ViewSelector):
    """
    The `LLMViewSelector` utilises LLMs to select the most suitable view to answer the user question.

    Its primary function is to determine the optimal view that can effectively be used to answer a user's question.

    The method used to select the most relevant view is `self.select_view`.
    It formats views using view.name: view.description format and then calls LLM Client,
    ultimately returning the name of the most suitable view.
    """

    def __init__(self, llm: LLM, prompt_template: Optional[Prompt] = None) -> None:
        """
        Constructs a new LLMViewSelector instance.

        Args:
            llm: LLM used to generate IQL
            prompt_template: template for the prompt used for the view selection
        """
        self._llm = llm
        self._prompt_template = prompt_template or ViewSelectionPrompt

    async def select_view(
        self,
        question: str,
        views: Dict[str, str],
        llm_options: Optional[Options] = None,
    ) -> str:
        """
        Based on user question and list of available views select the most relevant one by prompting LLM.

        Args:
            question: user question asked in the natural language e.g "Do we have any data scientists?"
            views: dictionary of available view names with corresponding descriptions.
            llm_options: options to use for the LLM client.

        Returns:
            The most relevant view name.

        Raises:
            LLMError: If LLM text generation fails.
        """

        selected_view = await self._llm.generate(
            self._prompt_template(ViewSelectionPromptInput(question=question, views=views)),
            options=llm_options,
        )
        return selected_view
