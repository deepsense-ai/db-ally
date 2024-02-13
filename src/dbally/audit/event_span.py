from contextlib import contextmanager


class EventSpan:

    def __init__(self):
        self._data = None

    def __call__(self, data: dict):
        self._data = data
