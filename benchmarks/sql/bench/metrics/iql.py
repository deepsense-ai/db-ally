from typing import Any, Dict, List

from dbally.collection.exceptions import NoViewFoundError
from dbally.iql._exceptions import IQLError, IQLFunctionNotExists
from dbally.iql_generator.prompt import UnsupportedQueryError

from ..pipeline import EvaluationResult
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
        iql_results = [
            result
            for result in results
            if result.prediction.iql is not None or isinstance(result.prediction.exception, NoViewFoundError)
        ]
        return {
            "EM_IQL": (
                sum(result.prediction.iql == result.reference.iql for result in iql_results) / len(iql_results)
                if iql_results
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
        supported_queries = [result for result in results if result.prediction.iql is not None]
        return {
            "VAL_IQL": (
                sum(not isinstance(result.prediction.exception, IQLError) for result in supported_queries)
                / len(supported_queries)
                if supported_queries
                else 0.0
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
        iql_queries = [
            result
            for result in results
            if result.prediction.iql is not None or isinstance(result.prediction.exception, UnsupportedQueryError)
        ]
        return {
            "UNSUPP_IQL": (
                sum(isinstance(result.prediction.exception, UnsupportedQueryError) for result in iql_queries)
                / len(iql_queries)
                if iql_queries
                else 0.0
            )
        }


class HallucinatedIQL(Metric):
    """
    Ratio of hallucinated IQL queries.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the hallucinated IQL ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Hallucinated queries ratio.
        """
        supported_queries = [result for result in results if result.prediction.iql is not None]
        return {
            "HAL_IQL": (
                sum(isinstance(result, IQLFunctionNotExists) for result in supported_queries) / len(supported_queries)
                if supported_queries
                else 0.0
            )
        }


class NoViewFound(Metric):
    """
    Ratio of queries with no view found.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the ratio of queries with no view found.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of queries with no view found.
        """
        return {
            "NO_VIEW": sum(isinstance(result.prediction.exception, NoViewFoundError) for result in results)
            / len(results)
            if results
            else 0.0
        }
