from typing import Any, Optional

from dbally.data_models.audit import LLMEvent


class EventSpan:
    """Helper class for logging events."""

    data: Optional[Any]

    def __init__(self) -> None:
        self.data = None

    def __call__(self, data: LLMEvent) -> None:
        """
        Call method for logging events.

        Args:
            data: Event data.
        """

        self.data = data
