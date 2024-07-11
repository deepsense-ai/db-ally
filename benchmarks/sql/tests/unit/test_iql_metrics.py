from iql.metrics import (
    _count_hallucinated_methods_for_single_example,
    calculate_hallucinated_filters,
    calculate_invalid_iql,
    calculate_valid_iql,
)
from results import TextToIQLResult

from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping

ALLOWED_METHODS = [
    ExposedFunction(
        name="filter_by_name",
        description="",
        parameters=[MethodParamWithTyping(name="name", type=str)],
    )
]

VALID_IQL = "filter_by_name('Cody Brown') or filter_by_name('Linda Smith')"
IQL_WITH_HALLUCINATED_FILTERS = "filter_by_name('Cody Brown') and filter_by_age(100)"
IQL_WITH_SYNTAX_ERROR = "filter_by_name('Cody Brown'"


def test_count_hallucinated_methods_for_single_example() -> None:
    hallucinated_methods, total_methods = _count_hallucinated_methods_for_single_example(
        IQL_WITH_HALLUCINATED_FILTERS, [method.name for method in ALLOWED_METHODS]
    )
    assert hallucinated_methods == 1
    assert total_methods == 2

    hallucinated_methods, total_methods = _count_hallucinated_methods_for_single_example(
        VALID_IQL, [method.name for method in ALLOWED_METHODS]
    )
    assert hallucinated_methods == 0
    assert total_methods == 2


def test_calculate_hallucinated_filters() -> None:
    dataset = [
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=IQL_WITH_HALLUCINATED_FILTERS),
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=VALID_IQL),
    ]
    hallucinated_filters_ratio = calculate_hallucinated_filters(dataset, ALLOWED_METHODS)
    assert hallucinated_filters_ratio == 0.25


async def test_calculate_invalid_iql() -> None:
    dataset = [
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=IQL_WITH_SYNTAX_ERROR),
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=VALID_IQL),
    ]

    syntax_errors_ratio = await calculate_invalid_iql(dataset, ALLOWED_METHODS)
    assert syntax_errors_ratio == 0.5


async def test_calculate_valid_iql() -> None:
    dataset = [
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=IQL_WITH_SYNTAX_ERROR),
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=VALID_IQL),
        TextToIQLResult(question="", ground_truth_iql="", predicted_iql=IQL_WITH_HALLUCINATED_FILTERS),
    ]

    valid_iql_ratio = await calculate_valid_iql(dataset, ALLOWED_METHODS)
    assert valid_iql_ratio >= 0.333 and valid_iql_ratio <= 0.334
