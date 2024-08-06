from typing import Any, Dict, List

from ..pipelines import EvaluationResult
from .base import Metric


class ViewSelectionAccuracy(Metric):
    """
    View selection accuracy is the proportion of correct view selections out of all view selection attempts.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the view selection accuracy.

        Args:
            results: List of evaluation results.

        Returns:
            View selection accuracy.
        """
        return {
            "VIEW/ACC": (
                sum(result.reference.view_name == result.prediction.view_name for result in results) / len(results)
                if results
                else None
            )
        }


class ViewSelectionPrecision(Metric):
    """
    View selection precision is proportion of correct view selections out of all cases where a view was selected.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the view selection precision.

        Args:
            results: List of evaluation results.

        Returns:
            View selection precision.
        """
        results = [result for result in results if result.prediction.view_name]
        return {
            "VIEW/PRECISION": (
                sum(result.prediction.view_name == result.reference.view_name for result in results) / len(results)
                if results
                else None
            )
        }


class ViewSelectionRecall(Metric):
    """
    View selection recall is proportion of correct view selections out of all cases where a view should have
    been selected.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the view selection recall.

        Args:
            results: List of evaluation results.

        Returns:
            View selection recall.
        """
        results = [
            result
            for result in results
            if result.prediction.view_name is None
            and result.reference.view_name
            or result.prediction.view_name == result.reference.view_name
        ]
        return {
            "VIEW/RECALL": (
                sum(result.prediction.view_name == result.reference.view_name for result in results) / len(results)
                if results
                else None
            )
        }
