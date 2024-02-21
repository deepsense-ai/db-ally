import random
from typing import Dict

from dbally.audit.event_tracker import EventTracker
from dbally.view_selection.base import ViewSelector


class RandomViewSelector(ViewSelector):
    """
    Mock View Selector selecting a random view.
    """

    async def select_view(self, question: str, views: Dict[str, str], event_tracker: EventTracker) -> str:
        """
        Dummy implementation returning random view.

        Args:
            question: user question.
            views: dictionary of available view names with corresponding descriptions.
            event_tracker: event store used to audit the selection process.

        Returns:
            random view name.
        """
        selected = random.choice(list(views.keys()))  # nosec
        print(f"For question: {question} I've randomly selected view: {selected}")
        return selected
