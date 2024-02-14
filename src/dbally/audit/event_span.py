from dbally.data_models.audit import LLMEvent


class EventSpan:
    """Helper class for logging events."""

    def __call__(self, data: LLMEvent) -> None:
        """
        Call method for logging events.

        Args:
            data: Event data.
        """

        self.data = data  # pylint: disable=attribute-defined-outside-init
