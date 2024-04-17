import ast
from typing import Dict, List, Tuple

from dbally_benchmark.iql.iql_result import IQLResult
from dbally_benchmark.iql.method_call_visitor import MethodCallVisitor
from loguru import logger

from dbally.iql._exceptions import IQLError, IQLUnsupportedSyntaxError
from dbally.iql._query import IQLQuery
from dbally.views.structured import ExposedFunction


def _count_hallucinated_methods_for_single_example(iql: str, allowed_methods: List[str]) -> Tuple[int, int]:
    try:
        predicted_methods = MethodCallVisitor.get_method_calls(ast.parse(iql))

        hallucinated_methods_count = 0

        for method in predicted_methods:
            if method not in allowed_methods:
                hallucinated_methods_count += 1

        return hallucinated_methods_count, len(predicted_methods)
    except:  # noqa: E722 pylint: disable=bare-except
        return 0, 0


def calculate_hallucinated_filters_for_dataset(dataset: List[IQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of hallucinated filters for a given dataset.

    Args:
        dataset: List containing IQLResult objects that
        represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Hallucinated filters ratio.
    """

    hallucinated_filters_count = 0
    total_filters_count = 0

    allowed_filters = [filter.name for filter in filter_list]

    for example in dataset:
        hallucinated_filters, total_filters = _count_hallucinated_methods_for_single_example(
            example.iql_filters, allowed_filters
        )
        hallucinated_filters_count += hallucinated_filters
        total_filters_count += total_filters

    if total_filters_count == 0:
        return 0

    return hallucinated_filters_count / total_filters_count


async def calculate_valid_iql(dataset: List[IQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of valid IQL queries for a given dataset.

    Args:
        dataset: List containing IQLResult objects that
        represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Valid IQL ratio.
    """

    valid_iql = 0

    for example in dataset:
        try:
            await IQLQuery.parse(example.iql_filters, filter_list)
            valid_iql += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning(f"Error while parsing IQL: {example.iql_filters}\n{exc}")

    return valid_iql / len(dataset)


async def calculate_syntax_errors(dataset: List[IQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of syntax errors for a given dataset.

    Args:
        dataset: List containing IQLResult objects that
        represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Syntax errors ratio.
    """

    syntax_errors = 0

    filtered_dataset = [example for example in dataset if example.iql_filters != "UNSUPPORTED_QUERY"]

    for example in filtered_dataset:
        try:
            await IQLQuery.parse(example.iql_filters, filter_list)
        except (IQLError, IQLUnsupportedSyntaxError, SyntaxError):
            syntax_errors += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # I haven't figured out yet how to handle it better :(
            logger.warning(f"Error while parsing IQL: {example.iql_filters}\n{exc}")

    return syntax_errors / len(filtered_dataset)


async def calculate_dataset_metrics(dataset: List[IQLResult], filter_list: List[ExposedFunction]) -> Dict[str, float]:
    """
    Calculates metrics for a given dataset. The following metrics are being calculated: valid IQL,
    ratio of hallucinated filters and ratio of IQLs contained syntax error.

    Args:
        dataset: List containing IQLResult objects that
        represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Dictionary containing metrics.
    """

    metrics = {
        "valid_iql": await calculate_valid_iql(dataset, filter_list),
        "hallucinated_filters": calculate_hallucinated_filters_for_dataset(dataset, filter_list),
        "syntax_errors": await calculate_syntax_errors(dataset, filter_list),
    }

    return metrics
