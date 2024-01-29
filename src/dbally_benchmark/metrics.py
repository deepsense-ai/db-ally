import asyncio
from typing import Dict, List

from dbally.db_connectors.base import DBConnector
from dbally_benchmark.dataset import Text2SQLResult
from dbally_benchmark.utils import batch


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


async def _check_exec_acc(example: Text2SQLResult, db_connector: DBConnector) -> bool:
    gt_query_result = await db_connector.run_query(example.ground_truth_sql)
    try:
        pred_query_result = await db_connector.run_query(example.predicted_sql)
    except:  # noqa: E722, pylint: disable=bare-except
        return False

    # TODO: Add some postprocessing like sorting columns and rows.
    return gt_query_result.rows == pred_query_result.rows


async def calculate_exec_acc(dataset: List[Text2SQLResult], db_connector: DBConnector) -> float:
    """
    Calculates execution accuracy score i.e. the proportion of examples in the evaluation set for
    which the executed results of both the predicted and ground-truth SQLs are identical.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        db_connector: DBConnector.

    Returns:
        Execution accuracy score.
    """

    rows_matches = 0

    for group in batch(dataset, 5):
        results = await asyncio.gather(*[_check_exec_acc(example, db_connector) for example in group])

        for result in results:
            rows_matches += result

    return rows_matches / len(dataset)


async def _check_valid_sql(example: Text2SQLResult, db_connector: DBConnector) -> bool:
    try:
        await db_connector.run_query(example.predicted_sql)
    except:  # noqa: E722, pylint: disable=bare-except
        return False
    return True


async def calculate_valid_sql(dataset: List[Text2SQLResult], db_connector: DBConnector) -> float:
    """
    Calculates the proportion of examples in the evaluation set for
    which the predicted SQLs are correct SQL queries.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        db_connector: DBConnector.

    Returns:
        Valid SQL score.
    """

    valid_sqls = 0

    for group in batch(dataset, 5):
        results = await asyncio.gather(*[_check_valid_sql(example, db_connector) for example in group])

        for result in results:
            valid_sqls += result

    return valid_sqls / len(dataset)


async def _calculate_ves_for_signle_example(
    example: Text2SQLResult, db_connector: DBConnector, reps: int = 100
) -> float:
    ves = 0
    exec_acc_score = await _check_exec_acc(example, db_connector)

    if exec_acc_score is False:
        return ves

    for group in batch([example] * reps, 5):
        gt_results = await asyncio.gather(*[db_connector.run_query(example.ground_truth_sql) for example in group])
        pred_results = await asyncio.gather(*[db_connector.run_query(example.predicted_sql) for example in group])

        for gt_result, pred_result in zip(gt_results, pred_results):
            ves += (gt_result.execution_time / pred_result.execution_time) ** (1 / 2)

    return ves / reps


async def calculate_ves(dataset: List[Text2SQLResult], db_connector: DBConnector) -> float:
    """
    Calculates valid efficiency score that measures the efficiency of valid SQLs generated
    by models. More details about this metric can be found here: https://arxiv.org/pdf/2305.03111.pdf.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        db_connector: DBConnector.

    Returns:
        Valid efficiency score.
    """

    total_ves: float = 0

    for example in dataset:
        ves = await _calculate_ves_for_signle_example(example, db_connector)
        total_ves += ves

    return total_ves / len(dataset)


async def calculate_dataset_metrics(dataset: List[Text2SQLResult], db_connector: DBConnector) -> Dict[str, float]:
    """
    Calculates Text2SQL evaluation metrics for a given dataset.

    Args:
        dataset: List containing Text2SQLResult objects that
        represents (ground truth query, predicted query).
        db_connector: DBConnector.

    Returns:
        Dictionary containing: exact match, valid SQL, execution accuracy and valid efficiency score..
    """

    metrics = {
        "exact_match": calculate_exact_match(dataset),
        "valid_sql": await calculate_valid_sql(dataset, db_connector),
        "execution_accuracy": await calculate_exec_acc(dataset, db_connector),
        "valid_efficiency_score": await calculate_ves(dataset, db_connector),
    }

    return metrics
