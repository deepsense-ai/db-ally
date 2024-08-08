from dspy import ChainOfThought, Module, Prediction
from tuning.signatures.filters import CheckQuestionFiltering


class FilteringAssessor(Module):
    """
    Program that assesses whether a question requires filtering.
    """

    def __init__(self) -> None:
        super().__init__()
        self.decide_cot = ChainOfThought(CheckQuestionFiltering)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires filtering.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide_cot(question=question).decision
        return Prediction(decision=decision.lower() == "true")
