from typing import List

import pytest

from benchmarks.sql.bench.metrics.iql import ExactMatchIQL, ValidIQL
from benchmarks.sql.bench.pipeline import EvaluationResult, ExecutionResult


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
    assert metric.compute(evaluation_results) == 0.5


def test_valid_iql(evaluation_results):
    metric = ValidIQL()
    assert metric.compute(evaluation_results) == 1
