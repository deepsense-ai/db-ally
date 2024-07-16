from typing import List

from dbally.views.freeform.text2sql.exceptions import Text2SQLError

from ..pipelines.base import EvaluationResult
from .base import Metric


class ExactMatchSQL(Metric):
    """
    Ratio of predicated queries that are identical to the ground truth ones.
    """

    name: str = "EM_SQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        return sum(result.prediction.sql == result.reference.sql for result in results) / len(results)


class ValidSQL(Metric):
    """
    Ratio of valid SQL queries for a given results.
    """

    name: str = "VAL_SQL"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the valid SQL ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Valid IQL ratio.
        """
        supported_queries = [result for result in results if result.prediction.sql is not None]
        return sum(not isinstance(result.prediction.exception, Text2SQLError) for result in supported_queries) / len(
            supported_queries
        )


class ExecutionAccuracy(Metric):
    """
    Execution accuracy score i.e. the proportion of examples in the evaluation set for
    which the executed results of both the predicted and ground-truth SQLs are identical.
    """

    name: str = "EX"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the execution accuracy score.

        Args:
            results: List of evaluation results.

        Returns:
            Execution accuracy score.
        """
        return 0.0


class ValidEfficiencyScore(Metric):
    """
    Valid efficiency score measures the efficiency of valid SQLs generated
    by models. More details about this metric can be found here: https://arxiv.org/pdf/2305.03111.pdf.
    """

    name: str = "VES"

    def compute(self, results: List[EvaluationResult]) -> float:
        """
        Calculates the valid efficiency score.

        Args:
            results: List of evaluation results.

        Returns:
            Valid efficiency score.
        """
        return 0.0
