from typing import Optional

from dbally.data_models.audit import LLMEvent


class EventSpan:
    """Helper class for logging events."""

    def __init__(self) -> None:
        self.data: Optional[LLMEvent] = None

    def __call__(self, data: Optional[LLMEvent]) -> None:
        """
        Call method for logging events.

        Args:
            data: Event data.
        """

        self.data = data
