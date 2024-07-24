from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock

import pytest

from benchmarks.sql.bench.metrics import ExactMatchIQL, ExecutionAccuracy, ValidIQL
from benchmarks.sql.bench.pipelines import EvaluationResult, ExecutionResult


@dataclass
class MockDataConfig:
    db_url: str = "sqlite:///:memory:"


@dataclass
class MockConfig:
    data: MockDataConfig = MockDataConfig()


@pytest.fixture
def evaluation_results() -> List[EvaluationResult]:
    return [
        EvaluationResult(
            question="question1",
            reference=ExecutionResult(iql="filter_by_column1(10)"),
            prediction=ExecutionResult(iql="filter_by_column1(10)"),
        ),
        EvaluationResult(
            question="question2",
            reference=ExecutionResult(iql="filter_by_column2(20)"),
            prediction=ExecutionResult(iql="filter_by_column2(30)"),
        ),
        EvaluationResult(
            question="question3",
            reference=ExecutionResult(iql="filter_by_column3('Test')"),
            prediction=ExecutionResult(iql="filter_by_column3(30)"),
        ),
        EvaluationResult(
            question="question4",
            reference=ExecutionResult(iql="filter_by_column4(40)"),
            prediction=ExecutionResult(iql="filter_by_column4(40)"),
        ),
    ]


def test_exact_match_iql(evaluation_results: List[EvaluationResult]) -> None:
    metric = ExactMatchIQL()
    scores = metric.compute(evaluation_results)
    assert scores["EM_IQL"] == 0.5


def test_valid_iql(evaluation_results) -> None:
    metric = ValidIQL()
    scores = metric.compute(evaluation_results)
    assert scores["VAL_IQL"] == 1.0


@pytest.mark.parametrize(
    "acc, avg_times, expected_ex, expected_ves",
    [
        ([True, False, True, True], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1], 0.75, 0.75),
        ([True, True, True, True], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1], 1.0, 1.0),
        ([False, False, False, False], [1.2, 1.2, 12.2, 12.2, 13.2, 13.2, 232.1, 232.1], 0.0, 0.0),
        ([True, False, True, True], [1.2, 3.2, 12.2, 15.2, 13.2, 17.2, 232.1, 287.1], 0.75, 0.5960767767585372),
        ([True, False, True, True], [3.2, 1.2, 15.2, 12.2, 17.2, 13.2, 287.1, 232.1], 0.75, 0.9726740826467557),
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
