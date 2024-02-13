import abc
from abc import ABC
import datetime
from loguru import logger

class CLIEventHandler:
    
    def start(self, user_input: dict):
        pass

    def notify(self, event: dict):
        logger.info(event)

    def end(self, output: dict):
        pass
