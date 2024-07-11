import ast
from typing import List, Tuple

from iql.method_call_visitor import MethodCallVisitor
from loguru import logger
from results import TextToIQLResult

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


def calculate_hallucinated_filters(results: List[TextToIQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of hallucinated filters for a given results.

    Args:
        results: List containing TextToIQLResult objects that represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Hallucinated filters ratio.
    """

    hallucinated_filters_count = 0
    total_filters_count = 0

    allowed_filters = [filter.name for filter in filter_list]

    for example in results:
        hallucinated_filters, total_filters = _count_hallucinated_methods_for_single_example(
            example.predicted_iql, allowed_filters
        )
        hallucinated_filters_count += hallucinated_filters
        total_filters_count += total_filters

    if total_filters_count == 0:
        return 0

    return hallucinated_filters_count / total_filters_count


async def calculate_valid_iql(results: List[TextToIQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of valid IQL queries for a given results.

    Args:
        results: List containing TextToIQLResult objects that represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Valid IQL ratio.
    """

    valid_iql = 0

    for example in results:
        try:
            await IQLQuery.parse(example.predicted_iql, filter_list)
            valid_iql += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning(f"Error while parsing IQL: {example.predicted_iql}\n{exc}")

    return valid_iql / len(results)


def calculate_exact_match(results: List[TextToIQLResult]) -> float:
    """
    For a results, it calculates the ratio of predicated queries that are identical
    to the ground truth ones.

    Args:
        results: List containing Text2SQLResult objects that represents ground truth query, predicted query.

    Returns:
        The ratio of predicated queries that are identical to the ground truth ones.
    """
    exact_query_matches = 0

    for example in results:
        if example.ground_truth_iql == example.predicted_iql:
            exact_query_matches += 1

    return exact_query_matches / len(results)


async def calculate_invalid_iql(results: List[TextToIQLResult], filter_list: List[ExposedFunction]) -> float:
    """
    Calculates the ratio of syntax errors for a given results.

    Args:
        results: List containing TextToIQLResult objects that represents predicted filters.
        filter_list: List of allowed filters.

    Returns:
        Syntax errors ratio.
    """
    syntax_errors = 0

    filtered_results = [result for result in results if result.predicted_iql != "UNSUPPORTED_QUERY"]

    for result in filtered_results:
        try:
            await IQLQuery.parse(result.predicted_iql, filter_list)
        except (IQLError, IQLUnsupportedSyntaxError, SyntaxError):
            syntax_errors += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # I haven't figured out yet how to handle it better :(
            logger.warning(f"Error while parsing IQL: {result.predicted_iql}\n{exc}")

    return syntax_errors / len(filtered_results)


def calculate_unsupported_iql(results: List[TextToIQLResult]) -> float:
    """
    Calculates the ratio of unsupported queries for a given results.

    Args:
        results: List containingTextToTextToIQLResult objects that represents predicted filters.

    Returns:
        Unsupported queries ratio.
    """
    unsupported_queries = 0

    for result in results:
        if result.predicted_iql == "UNSUPPORTED_QUERY":
            unsupported_queries += 1

    return unsupported_queries / len(results)
