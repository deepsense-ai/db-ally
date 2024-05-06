from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from .ddl import DDL

# TODO IN THIS FILE WE DEFINE ALL POSSIBLE AGENTS WE THINK OF?
# We could potentially use langgraph here or create simple sequential agents

# TODO WHERE TO PUT FEW-SHOT PROMPTS? THESE ARE AN ATTRIBUTE OF THE ENTIRE QUERY NOT THE DDL.


@dataclass
class AgentResult:
    """Dataclass that stores the result of an agent execution"""

    ddl: DDL = None
    fmt: Dict = {}
    sql: str = ""


class Text2SQLAgent(ABC):
    """Abstract class for all agents that are used in the text2sql pipeline"""

    @abstractmethod
    def process(self, current_result: AgentResult) -> AgentResult:
        """Processes the previous AgentResult and returns the result of the agent

        Args:
            current_result: The result of the previous agent

        Returns:
            AgentResult: The result of the agent
        """
