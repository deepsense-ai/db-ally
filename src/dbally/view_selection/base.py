import abc
from typing import Dict

from dbally.audit.event_tracker import EventTracker


class ViewSelector(abc.ABC):
    """Base class for view selectors."""

    @abc.abstractmethod
    async def select_view(self, question: str, views: Dict[str, str], event_tracker: EventTracker) -> str:
        """
        Based on user question and list of available views select the most relevant one.

        Args:
            question: user question asked in the natural language e.g "Do we have any data scientists?"
            views: dictionary of available view names with corresponding descriptions.
            event_tracker: event tracker used to audit the selection process.

        Returns:
            The most relevant view name.
        """
