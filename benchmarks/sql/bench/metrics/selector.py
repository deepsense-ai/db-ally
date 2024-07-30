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
            "VIEW/ACC": (
                sum(result.reference.view_name == result.prediction.view_name for result in results) / len(results)
                if results
                else None
            )
        }


class ViewSelectionPrecision(Metric):
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
