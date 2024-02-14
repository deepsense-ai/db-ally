import random
from typing import Dict

from dbally.audit.event_store import EventStore
from dbally.view_selection.base import ViewSelector


class RandomViewSelector(ViewSelector):
    """
    Mock View Selector selecting a random view.
    """

    async def select_view(self, question: str, views: Dict[str, str], event_store: EventStore) -> str:
        """
        Dummy implementation returning random view.

        Args:
            question: user question.
            views: dictionary of available view names with corresponding descriptions.
            event_store: event store used to audit the selection process.

        Returns:
            random view name.
        """
        selected = random.choice(list(views.keys()))  # nosec
        print(f"For question: {question} I've randomly selected view: {selected}")
        return selected
