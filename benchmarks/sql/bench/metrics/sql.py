import time
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from ..pipelines import EvaluationResult
from .base import Metric


class SQLExactMatch(Metric):
    """
    Exact match ratio i.e. the proportion of examples in the evaluation set for which
    the predicted SQL is identical to the ground truth SQL.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            The exact match ratio.
        """
        return {
            "SQL/EM": (
                sum(result.prediction.sql == result.reference.sql for result in results) / len(results)
                if results
                else 0.0
            )
        }


class _DBMixin:
    """
    Mixin class for database operations.
    """

    def __init__(self, config: Dict, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)
        self.dbs = {db: create_engine(f"sqlite:///data/{db}.db") for db in config.data.db_ids}

    def _execute_query(self, query: str, db_id: str) -> List[Dict[str, Any]]:
        """
        Execute the given query on the database.

        Args:
            query: The query to be executed.

        Returns:
            The query results.
        """
        with self.dbs[db_id].connect() as connection:
            rows = connection.execute(text(query)).fetchall()
        return [dict(row._mapping) for row in rows]  # pylint: disable=protected-access

    def _avarage_execution_time(self, query: str, db_id: str, n: int = 100) -> float:
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
            self._execute_query(query, db_id)
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
            "EX": len(accurate_results) / len(results) if results else None,
            "VES": sum(
                (
                    self._avarage_execution_time(result.reference.sql, result.db_id)
                    / self._avarage_execution_time(result.prediction.sql, result.db_id)
                )
                ** 0.5
                for result in accurate_results
            )
            / len(results)
            if results
            else None,
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
            ref_results = self._execute_query(result.reference.sql, result.db_id)
            pred_results = self._execute_query(result.prediction.sql, result.db_id)
        except SQLAlchemyError:
            return False

        reference = pd.DataFrame(ref_results)
        prediction = pd.DataFrame(pred_results)

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
