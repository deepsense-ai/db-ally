class EventSpan:
    """Helper class for logging events."""

    def __init__(self):
        self.data = None

    def __call__(self, data: dict):
        self.data = data
