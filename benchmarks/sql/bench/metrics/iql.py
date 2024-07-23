from typing import Any, Dict, List

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError

from ..pipelines import EvaluationResult
from .base import Metric


class ExactMatchIQL(Metric):
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
        results = [result for result in results if result.prediction.iql is not None]
        return {
            "EM_IQL": (
                sum(result.prediction.iql == result.reference.iql for result in results) / len(results)
                if results
                else None
            )
        }


class ExactMatchFiltersIQL(Metric):
    """
    Ration of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [result for result in results if result.prediction.iql is not None]
        return {
            "EM_FLT_IQL": (
                sum(result.prediction.iql.filters == result.reference.iql.filters for result in results) / len(results)
                if results
                else None
            )
        }


class ExactMatchAggregationIQL(Metric):
    """
    Ratio of predicated aggregation that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [result for result in results if result.prediction.iql is not None]
        return {
            "EM_AGG_IQL": (
                sum(result.prediction.iql.aggregation == result.reference.iql.aggregation for result in results)
                / len(results)
                if results
                else None
            )
        }


class UnsupportedIQL(Metric):
    """
    Ratio of unsupported IQL queries.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the unsupported IQL ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Unsupported queries ratio.
        """
        results = [
            result
            for result in results
            if result.prediction.iql is not None or isinstance(result.prediction.exception, UnsupportedQueryError)
        ]
        return {
            "UNSUPP_IQL": (
                sum(isinstance(result.prediction.exception, UnsupportedQueryError) for result in results) / len(results)
                if results
                else 0.0
            )
        }


class ValidIQL(Metric):
    """
    Ratio of valid IQL queries.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the valid IQL ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Valid IQL queries ratio.
        """
        results = [result for result in results if result.prediction.iql is not None]
        return {
            "VAL_IQL": (
                sum(not isinstance(result.prediction.exception, IQLError) for result in results) / len(results)
                if results
                else 0.0
            )
        }
