from typing import List

from ..pipelines.base import EvaluationResult
from .base import Metric


class ExactMatchSQL(Metric):
    """
    Computes the ratio of predicated queries that are identical to the ground truth ones.
    """

    name: str = "EM_SQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Computes the ratio of predicated queries that are identical to the ground truth ones.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        return sum(result.prediction.sql == result.reference.sql for result in results) / len(results)
