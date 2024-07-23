from typing import Any, Dict, List

from ..pipelines import EvaluationResult
from .base import Metric


class ViewSelectionAccuracy(Metric):
    """
    Ratio of predicated queries that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        return {
            "ACC_VIEW": (
                sum(result.prediction.view == result.reference.view for result in results) / len(results)
                if results
                else None
            )
        }
