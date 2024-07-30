from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock

import pytest

from benchmarks.sql.bench.metrics.iql import (
    FilteringAccuracy,
    FilteringPrecision,
    FilteringRecall,
    IQLFiltersAccuracy,
    IQLFiltersCorrectness,
    IQLFiltersParseability,
    IQLFiltersPrecision,
    IQLFiltersRecall,
)
from benchmarks.sql.bench.metrics.sql import ExecutionAccuracy, SQLExactMatch
from benchmarks.sql.bench.pipelines import EvaluationResult, ExecutionResult, IQLResult
from benchmarks.sql.bench.pipelines.base import IQL


@dataclass
class MockDataConfig:
    db_ids: str = "db_id"


@dataclass
class MockConfig:
    data: MockDataConfig = MockDataConfig()


@pytest.fixture
def evaluation_results() -> List[EvaluationResult]:
    return [
        EvaluationResult(
            db_id="db_id",
            question="question1",
            reference=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column1(10)",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column1 = 10",
            ),
            prediction=ExecutionResult(
                sql="SELECT * FROM table WHERE column1 = 10",
            ),
        ),
        EvaluationResult(
            db_id="db_id",
            question="question2",
            reference=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column2(20)",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column2 = 20",
            ),
            prediction=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column2(20)",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column2 = 30",
            ),
        ),
        EvaluationResult(
            db_id="db_id",
            question="question3",
            reference=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column3('TEST')",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column3 = 'TEST'",
            ),
            prediction=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column3('test')",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column3 = 'test'",
            ),
        ),
        EvaluationResult(
            db_id="db_id",
            question="question4",
            reference=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column4 = 40",
            ),
            prediction=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column4(40)",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column3 = 'TEST'",
            ),
        ),
        EvaluationResult(
            db_id="db_id",
            question="question5",
            reference=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source="filter_by_column5(50)",
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column5 = 50",
            ),
            prediction=ExecutionResult(
                iql=IQLResult(
                    filters=IQL(
                        source=None,
                        unsupported=True,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql="SELECT * FROM table WHERE column5 = 50",
            ),
        ),
    ]


def test_filtering_accuracy(evaluation_results: List[EvaluationResult]) -> None:
    metric = FilteringAccuracy()
    scores = metric.compute(evaluation_results)
    assert scores["DM/FLT/ACC"] == 0.5


def test_filtering_precision(evaluation_results: List[EvaluationResult]) -> None:
    metric = FilteringPrecision()
    scores = metric.compute(evaluation_results)
    assert scores["DM/FLT/PRECISION"] == 0.5


def test_filtering_recall(evaluation_results: List[EvaluationResult]) -> None:
    metric = FilteringRecall()
    scores = metric.compute(evaluation_results)
    assert scores["DM/FLT/RECALL"] == 0.6666666666666666


def test_iql_filters_accuracy(evaluation_results: List[EvaluationResult]) -> None:
    metric = IQLFiltersAccuracy()
    scores = metric.compute(evaluation_results)
    assert scores["IQL/FLT/ACC"] == 0.6666666666666666


def test_iql_filters_precision(evaluation_results: List[EvaluationResult]) -> None:
    metric = IQLFiltersPrecision()
    scores = metric.compute(evaluation_results)
    assert scores["IQL/FLT/PRECISION"] == 0.6666666666666666


def test_iql_filters_recall(evaluation_results: List[EvaluationResult]) -> None:
    metric = IQLFiltersRecall()
    scores = metric.compute(evaluation_results)
    assert scores["IQL/FLT/RECALL"] == 0.6666666666666666


def test_iql_filters_parseability(evaluation_results: List[EvaluationResult]) -> None:
    metric = IQLFiltersParseability()
    scores = metric.compute(evaluation_results)
    assert scores["IQL/FLT/PARSEABILITY"] == 1


def test_iql_filters_correctness(evaluation_results: List[EvaluationResult]) -> None:
    metric = IQLFiltersCorrectness()
    scores = metric.compute(evaluation_results)
    assert scores["IQL/FLT/CORRECTNESS"] == 0.5


def test_exact_match_sql(evaluation_results: List[EvaluationResult]) -> None:
    metric = SQLExactMatch()
    scores = metric.compute(evaluation_results)
    assert scores["SQL/EM"] == 0.4


@pytest.mark.parametrize(
    "acc, avg_times, expected_ex, expected_ves",
    [
        ([True, False, True, True, True], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1, 3, 3], 0.8, 0.8),
        ([True, True, True, True, True], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1, 3, 3], 1.0, 1.0),
        ([False, False, False, False, False], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1, 3, 3], 0.0, 0.0),
        (
            [True, False, True, True, True],
            [1.2, 3.2, 12.2, 15.2, 13.2, 17.2, 232.1, 287.1, 3, 3],
            0.8,
            0.6566867943411235,
        ),
        (
            [True, False, True, True, True],
            [3.2, 1.2, 15.2, 12.2, 17.2, 13.2, 287.1, 232.1, 3, 3],
            0.8,
            1.00057728666646,
        ),
    ],
)
def test_execution_accuracy(
    evaluation_results: List[EvaluationResult],
    acc: List[bool],
    avg_times: List[float],
    expected_ex: float,
    expected_ves: float,
) -> None:
    metric = ExecutionAccuracy(MockConfig())
    metric._execution_accuracy = MagicMock(side_effect=acc)
    metric._avarage_execution_time = MagicMock(side_effect=avg_times)
    scores = metric.compute(evaluation_results)
    assert scores["EX"] == expected_ex
    assert scores["VES"] == expected_ves
