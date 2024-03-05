from dbally.views.base import ExposedFunction, MethodParamWithTyping
from dbally_benchmark.iql.iql_result import IQLResult
from dbally_benchmark.iql.metrics import (
    _count_hallucinated_methods_for_single_example,
    calculate_hallucinated_filters_for_dataset,
    calculate_syntax_errors,
    calculate_valid_iql,
)

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


def test_count_hallucinated_methods_for_single_example():
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


def test_calculate_hallucinated_filters_for_dataset():
    dataset = [
        IQLResult(question="", iql_filters=IQL_WITH_HALLUCINATED_FILTERS, iql_actions=""),
        IQLResult(question="", iql_filters=VALID_IQL, iql_actions=""),
    ]

    hallucinated_filters_ratio = calculate_hallucinated_filters_for_dataset(dataset, ALLOWED_METHODS)
    assert hallucinated_filters_ratio == 0.25


def test_calculate_syntax_errors():
    dataset = [
        IQLResult(question="", iql_filters=IQL_WITH_SYNTAX_ERROR, iql_actions=""),
        IQLResult(question="", iql_filters=VALID_IQL, iql_actions=""),
    ]

    syntax_errors_ratio = calculate_syntax_errors(dataset, ALLOWED_METHODS, [])
    assert syntax_errors_ratio == 0.5


def test_calculate_valid_iql():
    dataset = [
        IQLResult(question="", iql_filters=IQL_WITH_SYNTAX_ERROR, iql_actions=""),
        IQLResult(question="", iql_filters=VALID_IQL, iql_actions=""),
        IQLResult(question="", iql_filters=IQL_WITH_HALLUCINATED_FILTERS, iql_actions=""),
    ]

    valid_iql_ratio = calculate_valid_iql(dataset, ALLOWED_METHODS, [])
    assert valid_iql_ratio >= 0.333 and valid_iql_ratio <= 0.334
