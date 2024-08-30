from typing import Type

from dspy import ChainOfThought, ChainOfThoughtWithHint, Module, Predict, Prediction

from ..signatures.iql import AggregationAssessor, FilteringAssessor


class FilteringAssessorPredict(Module):
    """
    Program that assesses whether a question requires filtering.
    """

    def __init__(self, signature: Type[FilteringAssessor]) -> None:
        super().__init__()
        self.decide = Predict(signature)

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

    def __init__(self, signature: Type[FilteringAssessor]) -> None:
        super().__init__()
        self.decide = ChainOfThought(signature)

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


class FilteringAssessorCoTH(Module):
    """
    Program that assesses whether a question requires filtering.
    """

    def __init__(self, signature: Type[FilteringAssessor]) -> None:
        super().__init__()
        self.decide = ChainOfThoughtWithHint(signature)

    def forward(self, question: str) -> Prediction:
        """
        Assess whether a question requires filtering.

        Args:
            question: The question to assess.

        Returns:
            The prediction.
        """
        decision = self.decide(
            question=question,
            hint="Look for words indicating data specific features.",
        ).decision
        return Prediction(decision=decision.lower() == "true")


class AggregationAssessorPredict(Module):
    """
    Program that assesses whether a question requires aggregation.
    """

    def __init__(self, signature: Type[AggregationAssessor]) -> None:
        super().__init__()
        self.decide = Predict(signature)

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

    def __init__(self, signature: Type[AggregationAssessor]) -> None:
        super().__init__()
        self.decide = ChainOfThought(signature)

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
