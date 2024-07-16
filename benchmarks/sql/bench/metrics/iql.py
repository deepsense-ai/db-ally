from typing import List

from dbally.iql._exceptions import IQLError, IQLFunctionNotExists
from dbally.iql_generator.prompt import UnsupportedQueryError

from ..pipelines.base import EvaluationResult
from .base import Metric


class ExactMatchIQL(Metric):
    """
    Ratio of predicated queries that are identical to the ground truth ones.
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


class ValidIQL(Metric):
    """
    Ratio of valid IQL queries.
    """

    name: str = "VAL_IQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the ratio of valid IQL queries for a given results.

        Args:
            results: List of evaluation results.

        Returns:
            Valid IQL queries ratio.
        """
        supported_queries = [result for result in results if result.prediction.iql is not None]
        if not supported_queries:
            return 0.0
        return sum(not isinstance(result.prediction.exception, IQLError) for result in supported_queries) / len(
            supported_queries
        )


class UnsupportedIQL(Metric):
    """
    Ratio of unsupported IQL queries.
    """

    name: str = "UNSUPP_IQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the ratio of unsupported queries for a given results.

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
        if not iql_queries:
            return 0.0
        return sum(isinstance(result.prediction.exception, UnsupportedQueryError) for result in iql_queries) / len(
            iql_queries
        )


class HallucinatedIQL(Metric):
    """
    Ratio of hallucinated IQL queries.
    """

    name: str = "HAL_IQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the ratio of hallucinated queries for a given results.

        Args:
            results: List of evaluation results.

        Returns:
            Hallucinated queries ratio.
        """
        supported_queries = [result for result in results if result.prediction.iql is not None]
        if not supported_queries:
            return 0.0
        return sum(isinstance(result, IQLFunctionNotExists) for result in supported_queries) / len(supported_queries)
