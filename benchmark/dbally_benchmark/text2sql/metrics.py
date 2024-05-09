import time
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd
from dbally_benchmark.text2sql.text2sql_result import Text2SQLResult
from dbally_benchmark.utils import batch
from sqlalchemy import Engine, text


@dataclass
class _ExecutionResult:
    """
    Represents the result of a single query execution
    """

    results: List[Dict[str, Any]]
    context: Dict[str, Any]
    execution_time: float


def _run_query(query: str, engine: Engine) -> _ExecutionResult:
    with engine.connect() as connection:
        start_time = time.monotonic()
        rows = connection.execute(text(query)).fetchall()
        execution_time = time.monotonic() - start_time

    return _ExecutionResult(
        results=[dict(row._mapping) for row in rows],  # pylint: disable=protected-access
        execution_time=execution_time,
        context={"sql": query},
    )


def calculate_exact_match(dataset: List[Text2SQLResult]) -> float:
    """
    For a dataset, it calculates the ratio of predicated queries that are identical
    to the ground truth ones.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).

    Returns:
        The ratio of predicated queries that are identical to the ground truth ones.
    """

    exact_query_matches = 0

    for example in dataset:
        if example.ground_truth_sql == example.predicted_sql:
            exact_query_matches += 1

    return exact_query_matches / len(dataset)


def _check_exec_acc(example: Text2SQLResult, engine: Engine) -> bool:
    gt_query_result = _run_query(example.ground_truth_sql, engine)
    try:
        pred_query_result = _run_query(example.predicted_sql, engine)
    except:  # noqa: E722, pylint: disable=bare-except
        return False

    df_gt = pd.DataFrame(gt_query_result.results)
    df = pd.DataFrame(pred_query_result.results)
    # If filtering works correctly, the number of rows will be the same
    # TODO: Sometimes a different number of rows is okay, e.g. if df has aggregated values that are expanded in gt
    if df_gt.shape[0] != df.shape[0]:
        return False
    # Returned view may have the same columns, or more columns than the ground truth
    if not df_gt.columns.isin(df.columns).all():
        return False
    # Check if dataframe equality, disregarding indexing and order
    # commented out way is also ok but slower. Leaving it here just in case
    # return df_gt.merge(df[df_gt.columns], how='outer', on=df_gt.columns.tolist(),
    #                    indicator='indicator').indicator.drop_duplicates().values.tolist() == ['both']
    df = df[df_gt.columns].sort_values(by=df_gt.columns.tolist()).reset_index(drop=True)
    df_gt = df_gt.sort_values(by=df_gt.columns.tolist()).reset_index(drop=True)
    return df.equals(df_gt)


def calculate_exec_acc(dataset: List[Text2SQLResult], engine: Engine) -> float:
    """
    Calculates execution accuracy score i.e. the proportion of examples in the evaluation set for
    which the executed results of both the predicted and ground-truth SQLs are identical.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        engine: Engine.

    Returns:
        Execution accuracy score.
    """

    rows_matches = 0

    for group in batch(dataset, 5):
        results = [_check_exec_acc(example, engine) for example in group]

        for result in results:
            rows_matches += result

    return rows_matches / len(dataset)


def _check_valid_sql(example: Text2SQLResult, engine: Engine) -> bool:
    try:
        _run_query(example.predicted_sql, engine)
    except:  # noqa: E722, pylint: disable=bare-except
        return False
    return True


def calculate_valid_sql(dataset: List[Text2SQLResult], engine: Engine) -> float:
    """
    Calculates the proportion of examples in the evaluation set for
    which the predicted SQLs are correct SQL queries.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        engine: Engine.

    Returns:
        Valid SQL score.
    """

    valid_sqls = 0

    for group in batch(dataset, 5):
        results = [_check_valid_sql(example, engine) for example in group]

        for result in results:
            valid_sqls += result

    return valid_sqls / len(dataset)


def _calculate_ves_for_single_example(example: Text2SQLResult, engine: Engine, reps: int = 5) -> float:
    ves = 0
    exec_acc_score = _check_exec_acc(example, engine)

    if exec_acc_score is False:
        return ves

    for group in batch([example] * reps, 5):
        gt_results = [_run_query(example.ground_truth_sql, engine) for example in group]
        pred_results = [_run_query(example.predicted_sql, engine) for example in group]

        for gt_result, pred_result in zip(gt_results, pred_results):
            ves += (gt_result.execution_time / pred_result.execution_time) ** (1 / 2)  # type: ignore

    return ves / reps


def calculate_ves(dataset: List[Text2SQLResult], engine: Engine) -> float:
    """
    Calculates valid efficiency score that measures the efficiency of valid SQLs generated
    by models. More details about this metric can be found here: https://arxiv.org/pdf/2305.03111.pdf.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        engine: Engine.

    Returns:
        Valid efficiency score.
    """

    total_ves: float = 0

    for example in dataset:
        ves = _calculate_ves_for_single_example(example, engine)
        total_ves += ves

    return total_ves / len(dataset)


def calculate_no_view_found_error_ratio(dataset: List[Text2SQLResult]) -> float:
    """
    Calculates ratio of NoViewFoundError for a given dataset.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).

    Returns:
        NoViewFoundError ratio.
    """

    total_no_view_found_error_ratio: float = 0

    for example in dataset:
        if example.predicted_sql == "NoViewFoundError":
            total_no_view_found_error_ratio += 1

    return total_no_view_found_error_ratio / len(dataset)


def calculate_undefined_error_ratio(dataset: List[Text2SQLResult]) -> float:
    """
    Calculates ratio of unspecified errors for a given dataset.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).

    Returns:
        Errors ratio.
    """

    total_no_view_found_error_ratio: float = 0

    for example in dataset:
        if example.predicted_sql == "Error":
            total_no_view_found_error_ratio += 1

    return total_no_view_found_error_ratio / len(dataset)


def calculate_unsupported_query_error_ratio(dataset: List[Text2SQLResult]) -> float:
    """
    Calculates ratio of UnsupportedQueryError for a given dataset.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).

    Returns:
        UnsupportedQueryError ratio.
    """

    total_unsupported_query_error_ratio: float = 0

    for example in dataset:
        if example.predicted_sql == "UnsupportedQueryError":
            total_unsupported_query_error_ratio += 1

    return total_unsupported_query_error_ratio / len(dataset)


def calculate_dataset_metrics(dataset: List[Text2SQLResult], engine: Engine) -> Dict[str, float]:
    """
    Calculates Text2SQL evaluation metrics for a given dataset.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        engine: Engine.

    Returns:
        Dictionary containing: exact match, no view found error ratio, undefined error ratio,
        unsupported query error ratio, valid SQL, execution accuracy
        and valid efficiency score.
    """

    metrics = {
        "valid_sql": calculate_valid_sql(dataset, engine),
        "no_view_found_error": calculate_no_view_found_error_ratio(dataset),
        "unsupported_query_error": calculate_unsupported_query_error_ratio(dataset),
        "undefined_error": calculate_undefined_error_ratio(dataset),
        "exact_match": calculate_exact_match(dataset),
        "execution_accuracy": calculate_exec_acc(dataset, engine),
        "valid_efficiency_score": calculate_ves(dataset, engine),
    }

    return metrics
