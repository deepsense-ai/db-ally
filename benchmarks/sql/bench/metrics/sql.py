import time
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from dbally.views.freeform.text2sql.exceptions import Text2SQLError

from ..pipeline import EvaluationResult
from .base import Metric


class ExactMatchSQL(Metric):
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
            "EM_SQL": (
                sum(result.prediction.sql == result.reference.sql for result in results) / len(results)
                if results
                else 0.0
            )
        }


class ValidSQL(Metric):
    """
    Ratio of valid SQL queries for a given results.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the valid SQL ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Valid IQL ratio.
        """
        supported_queries = [result for result in results if result.prediction.sql is not None]
        return {
            "VAL_SQL": (
                sum(not isinstance(result.prediction.exception, Text2SQLError) for result in supported_queries)
                / len(supported_queries)
                if supported_queries
                else 0.0
            )
        }


class _DBMixin:
    """
    Mixin class for database operations.
    """

    def __init__(self, config: Dict, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)
        self.db = create_engine(config.data.db_url)

    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute the given query on the database.

        Args:
            query: The query to be executed.

        Returns:
            The query results.
        """
        with self.db.connect() as connection:
            rows = connection.execute(text(query)).fetchall()
        return [dict(row._mapping) for row in rows]  # pylint: disable=protected-access

    def _avarage_execution_time(self, query: str, n: int = 100) -> float:
        """
        Execute the given query on the database n times and return the average execution time.

        Args:
            query: The query to be executed.
            n: The number of times to execute the query.

        Returns:
            The average execution time.
        """
        total_time = 0
        for _ in range(n):
            start_time = time.perf_counter()
            self._execute_query(query)
            total_time += time.perf_counter() - start_time
        return total_time / n


class ExecutionAccuracy(_DBMixin, Metric):
    """
    Execution accuracy score i.e. the proportion of examples in the evaluation set for
    which the executed results of both the predicted and ground-truth SQLs are identical.

    Valid efficiency score measures the efficiency of valid SQLs generated
    by models. More details about this metric can be found here: https://arxiv.org/pdf/2305.03111.pdf.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculates the execution accuracy score and valid efficiency score.

        Args:
            results: List of evaluation results.

        Returns:
            Execution accuracy score and valid efficiency score.
        """
        accurate_results = [result for result in results if self._execution_accuracy(result)]
        return {
            "EX": len(accurate_results) / len(results) if results else 0.0,
            "VES": sum(
                (
                    self._avarage_execution_time(result.reference.sql)
                    / self._avarage_execution_time(result.prediction.sql)
                )
                ** 0.5
                for result in accurate_results
            )
            / len(results)
            if results
            else 0.0,
        }

    def _execution_accuracy(self, result: EvaluationResult) -> bool:
        """
        Checks if the execution results of both the predicted and ground-truth SQLs are identical.

        Args:
            result: Evaluation result.

        Returns:
            True if the execution results are identical, False otherwise.
        """
        if result.prediction.sql is None:
            return False
        try:
            result.reference.results = self._execute_query(result.reference.sql)
            result.prediction.results = self._execute_query(result.prediction.sql)
        except SQLAlchemyError:
            return False

        reference = pd.DataFrame(result.reference.results)
        prediction = pd.DataFrame(result.prediction.results)

        # If filtering works correctly, the number of rows will be the same
        # TODO: Sometimes a different number of rows is okay, e.g. if df has aggregated values that are expanded in gt
        if reference.shape[0] != prediction.shape[0]:
            return False

        # Returned view may have the same columns, or more columns than the ground truth
        if not reference.columns.isin(prediction.columns).all():
            return False

        # Check if dataframe equality, disregarding indexing and order
        # commented out way is also ok but slower. Leaving it here just in case
        # return df_gt.merge(df[df_gt.columns], how='outer', on=df_gt.columns.tolist(),
        # indicator='indicator').indicator.drop_duplicates().values.tolist() == ['both']
        prediction = prediction[reference.columns].sort_values(by=reference.columns.tolist()).reset_index(drop=True)
        reference = reference.sort_values(by=reference.columns.tolist()).reset_index(drop=True)
        return prediction.equals(reference)
