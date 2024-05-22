import abc
from typing import Dict, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.llms.clients.base import LLMOptions


class ViewSelector(abc.ABC):
    """Base class for view selectors."""

    @abc.abstractmethod
    async def select_view(
        self,
        question: str,
        views: Dict[str, str],
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions] = None,
    ) -> str:
        """
        Based on user question and list of available views select the most relevant one.

        Args:
            question: user question asked in the natural language e.g "Do we have any data scientists?"
            views: dictionary of available view names with corresponding descriptions.
            event_tracker: event tracker used to audit the selection process.
            llm_options: options to use for the LLM client.

        Returns:
            The most relevant view name.
        """
