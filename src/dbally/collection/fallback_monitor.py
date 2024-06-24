from typing import Tuple, List, Dict

from dbally.audit.events import FallbackEvent


class FallbackMonitor:

    def __init__(self):
        self.fallback_log: Dict[Tuple[str, int], List[FallbackEvent]] = {}

    def add_fallback_event(self, question: str, start_time: int, fallback_event: FallbackEvent):
        if not self.fallback_log.get((question, start_time)):
            self.fallback_log[(question, start_time)] = [fallback_event]
        else:
            self.fallback_log[(question, start_time)].append(fallback_event)

    def number_of_fallback_queries(self) -> int:
        return len(self.fallback_log)

    def __str__(self):
        return f"Called fallbacks: {self.fallback_log}"
