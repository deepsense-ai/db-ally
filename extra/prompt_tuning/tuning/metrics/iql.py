from typing import Dict

from dspy import Prediction


def iql_dm(gold: Dict, pred: Prediction) -> int:
    """
    IQL decision metric.

    Args:
        gold: The ground truth data point.
        pred: The prediction.

    Returns:
        The decision metric.
    """
    return (
        ((gold["iql_filters"] is None and not gold["iql_filters_unsupported"]) and not pred.decision)
        or (gold["iql_filters"] is not None or gold["iql_filters_unsupported"])
        and pred.decision
    )
