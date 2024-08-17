from typing import Dict

from dspy import Prediction


def filtering_assess_acc(gold: Dict, pred: Prediction) -> bool:
    """
    IQL filtering decision metric.

    Args:
        gold: The ground truth data point.
        pred: The prediction.

    Returns:
        The filtering decision accuracy.
    """
    return ((gold["iql_filters"] is None and not gold["iql_filters_unsupported"]) and not pred.decision) or (
        (gold["iql_filters"] is not None or gold["iql_filters_unsupported"]) and pred.decision
    )


def aggregation_assess_acc(gold: Dict, pred: Prediction) -> bool:
    """
    IQL aggregation decision metric.

    Args:
        gold: The ground truth data point.
        pred: The prediction.

    Returns:
        The aggregation decision accuracy.
    """
    return ((gold["iql_aggregation"] is None and not gold["iql_aggregation_unsupported"]) and not pred.decision) or (
        (gold["iql_aggregation"] is not None or gold["iql_aggregation_unsupported"]) and pred.decision
    )
