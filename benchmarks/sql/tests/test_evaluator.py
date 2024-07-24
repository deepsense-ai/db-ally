from typing import Dict, List

import pytest

from benchmarks.sql.bench.evaluator import Evaluator


class MockDataLoader:
    async def load(self) -> List[str]:
        return ["data1", "data2"]


class MockMetricSet:
    def compute(self, results) -> Dict[str, float]:
        return {"accuracy": 0.95}


class MockEvaluationResult:
    def dict(self) -> Dict[str, str]:
        return {"result": "processed_data"}


class MockEvaluationPipeline:
    async def __call__(self, data) -> MockEvaluationResult:
        return MockEvaluationResult()


@pytest.mark.asyncio
async def test_compute() -> None:
    evaluator = Evaluator(task="test_task")
    dataloader = MockDataLoader()
    metrics = MockMetricSet()
    pipeline = MockEvaluationPipeline()

    result = await evaluator.compute(pipeline, dataloader, metrics)

    assert "metrics" in result
    assert "results" in result
    assert result["metrics"]["accuracy"] == 0.95
    assert len(result["results"]) == 2  # Assuming two data points were processed


@pytest.mark.asyncio
async def test_call_pipeline() -> None:
    evaluator = Evaluator(task="test_task")
    pipeline = MockEvaluationPipeline()
    dataset = [1, 2]

    results, perf_results = await evaluator._call_pipeline(pipeline, dataset)

    assert len(results) == len(dataset)  # Ensure all data was processed
    assert "total_time_in_seconds" in perf_results["time_perf"]


@pytest.mark.asyncio
def test_results_processor() -> None:
    evaluator = Evaluator(task="test_task")
    results = [MockEvaluationResult(), MockEvaluationResult()]

    processed_results = evaluator._results_processor(results)

    assert "results" in processed_results
    assert len(processed_results["results"]) == len(results)


@pytest.mark.asyncio
def test_compute_metrics() -> None:
    evaluator = Evaluator(task="test_task")
    metrics = MockMetricSet()
    results = [MockEvaluationResult(), MockEvaluationResult()]

    computed_metrics = evaluator._compute_metrics(metrics, results)

    assert "metrics" in computed_metrics
    assert computed_metrics["metrics"]["accuracy"] == 0.95


@pytest.mark.asyncio
def test_compute_time_perf() -> None:
    evaluator = Evaluator(task="test_task")
    start_time = 0
    end_time = 2
    num_samples = 100

    perf_metrics = evaluator._compute_time_perf(start_time, end_time, num_samples)

    assert perf_metrics["time_perf"]["total_time_in_seconds"] == 2
    assert perf_metrics["time_perf"]["samples_per_second"] == 50
    assert perf_metrics["time_perf"]["latency_in_seconds"] == 0.02
