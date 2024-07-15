from typing import List

from dbally.iql._exceptions import IQLError, IQLUnsupportedSyntaxError

from ..pipelines.base import EvaluationResult
from .base import Metric


class ExactMatchIQL(Metric):
    """
    Computes the ratio of predicated queries that are identical to the ground truth ones.
    """

    name: str = "EM_IQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Computes the ratio of predicated queries that are identical to the ground truth ones.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        return sum(result.prediction.iql == result.reference.iql for result in results) / len(results)


def exact_match(results: List[EvaluationResult]) -> float:
    """
    Computes the ratio of predicated queries that are identical to the ground truth ones.

    Args:
        results: List of evaluation results.

    Returns:
        Ratio of predicated queries that are identical to the ground truth ones.
    """
    return sum(result.prediction.iql == result.reference.iql for result in results) / len(results)


def valid_iql(results: List[EvaluationResult]) -> float:
    """
    Calculates the ratio of valid IQL queries for a given results.

    Args:
        results: List of evaluation results.

    Returns:
        Valid IQL queries ratio.
    """
    return sum(
        not isinstance(result.prediction.exception, (IQLError, IQLUnsupportedSyntaxError, SyntaxError))
        for result in results
    ) / len(results)


def invalid_iql(results: List[EvaluationResult]) -> float:
    """
    Calculates the ratio of invalid IQL queries for a given results.

    Args:
        results: List of evaluation results.

    Returns:
        Invalid IQL queries ratio.
    """

    return sum(isinstance(result.prediction.exception, (IQLError, SyntaxError)) for result in results) / len(results)


def unsupported_iql(results: List[EvaluationResult]) -> float:
    """
    Calculates the ratio of unsupported queries for a given results.

    Args:
        results: List of evaluation results.

    Returns:
        Unsupported queries ratio.
    """
    return sum(isinstance(result.prediction.exception, IQLUnsupportedSyntaxError) for result in results) / len(results)
