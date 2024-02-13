import random
from typing import Optional

from loguru import logger

from dbally.audit.event_handlers.base import EventHandler


class CLIEventHandler(EventHandler):

    def request_start(self, user_input: dict):
        logger.info("Request start: {user_input}")

    def event_start(self, event: dict) -> Optional[dict]:
        my_super_important_integer = random.randint(1, 100)
        logger.info(f"event_start [id={my_super_important_integer}] event={event}")
        return {
            "id": my_super_important_integer
        }

    def event_end(self, event: dict, start_event_payload: Optional[dict]) -> Optional[dict]:
        logger.info(f"event_end [id={start_event_payload['id']}] event={event}")

    def request_end(self, output: dict):
        logger.info("Request end: {output}")
