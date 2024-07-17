from unittest.mock import AsyncMock, MagicMock

import pytest

from benchmarks.sql.bench.evaluator import Evaluator


class MockPipeline:
    async def __call__(self, data):
        return ["mock_result"], {"mock_perf": "mock_value"}


class MockMetricSet:
    def compute(self, results):
        return {"mock_metric": "mock_value"}


class MockDataset:
    pass


class MockEvaluationResult:
    def dict(self):
        return {"mock_result_key": "mock_result_value"}


@pytest.mark.asyncio
async def test_compute():
    evaluator = Evaluator(task="test_task")
    pipe = MockPipeline()
    data = MockDataset()
    metrics = MockMetricSet()

    # Mocking the internal methods which are not the target of this test
    evaluator._call_pipeline = AsyncMock(return_value=(["mock_result"], {"mock_perf": "mock_value"}))
    evaluator._compute_metrics = MagicMock(return_value={"mock_metric": "mock_value"})
    evaluator._results_processor = MagicMock(return_value={"processed_results": "mock_processed_results"})

    expected_result = {
        "mock_perf": "mock_value",
        "mock_metric": "mock_value",
        "processed_results": "mock_processed_results",
    }

    result = await evaluator.compute(pipe, data, metrics)
    assert result == expected_result


@pytest.mark.asyncio
async def test_call_pipeline():
    evaluator = Evaluator(task="test_task")
    pipe = MockPipeline()
    data = MockDataset()

    results, perf_results = await evaluator._call_pipeline(pipe, data)

    assert len(results) == 2
    assert "mock_perf" in perf_results


def test_results_processor():
    evaluator = Evaluator(task="test_task")
    results = [MockEvaluationResult()]

    processed_results = evaluator._results_processor(results)

    assert "results" in processed_results
    assert processed_results["results"][0]["mock_result_key"] == "mock_result_value"


def test_compute_metrics():
    evaluator = Evaluator(task="test_task")
    metrics = MockMetricSet()
    results = [MockEvaluationResult()]

    computed_metrics = evaluator._compute_metrics(metrics, results)

    assert "metrics" in computed_metrics
    assert computed_metrics["metrics"]["mock_metric"] == "mock_value"


def test_compute_time_perf() -> None:
    evaluator = Evaluator(task="test_task")
    start_time = 0
    end_time = 10
    num_samples = 100

    perf_metrics = evaluator._compute_time_perf(start_time, end_time, num_samples)

    assert "time_perf" in perf_metrics
    assert perf_metrics["time_perf"]["total_time_in_seconds"] == 10
    assert perf_metrics["time_perf"]["samples_per_second"] == 10
    assert perf_metrics["time_perf"]["latency_in_seconds"] == 0.1
