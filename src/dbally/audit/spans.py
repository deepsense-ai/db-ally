from typing import Optional

from dbally.audit.events import Event


class EventSpan:
    """
    Helper class for logging events.
    """

    def __init__(self) -> None:
        self.data: Optional[Event] = None

    def __call__(self, data: Event) -> None:
        """
        Call method for logging events.

        Args:
            data: Event data.
        """
        self.data = data
