from dspy import ChainOfThought, Module, Predict, Prediction

from ..signatures.iql import CheckQuestionAggregation, CheckQuestionFiltering


class FilteringAssessorBaseline(Module):
    """
    Program that assesses whether a question requires filtering.
    """

    def __init__(self) -> None:
        super().__init__()
        self.decide = Predict(CheckQuestionFiltering)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires filtering.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide(question=question).decision
        return Prediction(decision=decision.lower() == "true")


class FilteringAssessorCoT(Module):
    """
    Program that assesses whether a question requires filtering.
    """

    def __init__(self) -> None:
        super().__init__()
        self.decide = ChainOfThought(CheckQuestionFiltering)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires filtering.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide(question=question).decision
        return Prediction(decision=decision.lower() == "true")


class AggregationAssessorBaseline(Module):
    """
    Program that assesses whether a question requires aggregation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.decide = Predict(CheckQuestionAggregation)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires aggregation.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide(question=question).decision
        return Prediction(decision=decision.lower() == "true")


class AggregationAssessorCoT(Module):
    """
    Program that assesses whether a question requires aggregation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.decide = ChainOfThought(CheckQuestionAggregation)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires aggregation.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide(question=question).decision
        return Prediction(decision=decision.lower() == "true")
