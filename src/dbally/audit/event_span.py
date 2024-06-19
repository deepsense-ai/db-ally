from typing import Any, Optional, Union

from dbally.audit.events import LLMEvent, SimilarityEvent


class EventSpan:
    """Helper class for logging events."""

    data: Optional[Any]

    def __init__(self) -> None:
        self.data = None

    def __call__(self, data: Union[LLMEvent, SimilarityEvent]) -> None:
        """
        Call method for logging events.

        Args:
            data: Event data.
        """

        self.data = data
