from abc import ABC, abstractmethod
from typing import Dict


class AbstractFewShotSelector(ABC):
    """
    Provides a selection of few-shot examples
    """

    def __init__(self, view) -> None:
        self.view = view

    @abstractmethod
    def get_examples(self) -> Dict[str, str]:
        """
        Lists all examples in a form of a dictionary, where questions are keys and answers are values.

        Returns:
            List of examples
        """
