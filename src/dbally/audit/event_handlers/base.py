import abc
from abc import ABC

class BaseEventHandler(ABC):
    
    @abc.abstractmethod
    def start(self, user_input: dict):
        pass
    
    @abc.abstractmethod
    def notify(self, event: dict):
        pass

    @abc.abstractmethod
    def end(self, output: dict):
        pass
