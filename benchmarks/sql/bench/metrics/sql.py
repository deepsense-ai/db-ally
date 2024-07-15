from typing import List

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from dbally.iql._exceptions import IQLError, IQLUnsupportedSyntaxError

from ..pipelines.base import EvaluationResult


def exact_match(results: List[EvaluationResult]) -> float:
    """
    Computes the ratio of predicated queries that are identical to the ground truth ones.

    Args:
        results: List of evaluation results.

    Returns:
        Ratio of predicated queries that are identical to the ground truth ones.
    """
    return sum(result.prediction.sql == result.reference.sql for result in results) / len(results)


def valid_sql(results: List[EvaluationResult]) -> float:
    """
    Calculates the ratio of valid SQL queries for a given results.

    Args:
        results: List of evaluation results.

    Returns:
        Valid IQL ratio.
    """
    return sum(
        not isinstance(result.prediction.exception, (IQLError, IQLUnsupportedSyntaxError, SyntaxError, SQLAlchemyError))
        for result in results
    ) / len(results)


def invalid_sql(results: List[EvaluationResult]) -> float:
    """
    Calculates the ratio of valid SQL queries for a given results.

    Args:
        results: List of evaluation results.

    Returns:
        Invalid IQL ratio.
    """

    return sum(
        isinstance(result.prediction.exception, (IQLError, IQLUnsupportedSyntaxError, SyntaxError, SQLAlchemyError))
        for result in results
    ) / len(results)


def _execution_accuracy(result: EvaluationResult) -> bool:
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
    #                    indicator='indicator').indicator.drop_duplicates().values.tolist() == ['both']
    prediction = prediction[reference.columns].sort_values(by=reference.columns.tolist()).reset_index(drop=True)
    reference = reference.sort_values(by=reference.columns.tolist()).reset_index(drop=True)
    return prediction.equals(reference)


def execution_accuracy(results: List[EvaluationResult]) -> float:
    """
    Calculates execution accuracy score i.e. the proportion of examples in the evaluation set for
    which the executed results of both the predicted and ground-truth SQLs are identical.

    Args:
        results: List of evaluation results.

    Returns:
        Execution accuracy score.
    """
    return sum(_execution_accuracy(result) for result in results) / len(results)


def _valid_efficiency_score(result: EvaluationResult) -> float:
    if _execution_accuracy(result) is False:
        return 0
    return (result.reference.execution_time_ns / result.prediction.execution_time_ns) ** 0.5


def valid_efficiency_score(results: List[EvaluationResult]) -> float:
    """
    Calculates valid efficiency score that measures the efficiency of valid SQLs generated
    by models. More details about this metric can be found here: https://arxiv.org/pdf/2305.03111.pdf.

    Args:
        results: List of evaluation results.

    Returns:
        Valid efficiency score.
    """
    return sum(_valid_efficiency_score(result) for result in results) / len(results)
