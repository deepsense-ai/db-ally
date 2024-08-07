import time
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Tuple

from datasets import Dataset
from tqdm.asyncio import tqdm

from .loaders import DataLoader
from .metrics.base import MetricSet
from .pipelines import EvaluationPipeline, EvaluationResult


class Evaluator:
    """
    Evaluator class.
    """

    def __init__(self, task: str) -> None:
        """
        Constructs the evaluator.

        Args:
            task: The task for the evaluator.
        """
        self.task = task

    async def compute(
        self,
        pipeline: Callable,
        dataloader: DataLoader,
        metrics: MetricSet,
    ) -> Dict[str, Any]:
        """
        Compute the evaluation results for the given pipeline and data.

        Args:
            pipeline: The pipeline to be evaluated.
            dataloader: The dataloader to load the data.
            metrics: The metrics to be computed.

        Returns:
            The evaluation results.
        """
        dataset = await dataloader.load()
        results, perf_results = await self._call_pipeline(pipeline, dataset)
        computed_metrics = self._compute_metrics(metrics, results)
        results = self._results_processor(results)

        result = {}
        result.update(perf_results)
        result.update(computed_metrics)
        result.update(results)
        return result

    async def _call_pipeline(
        self,
        pipe: EvaluationPipeline,
        dataset: Dataset,
    ) -> Tuple[List[EvaluationResult], Dict[str, Any]]:
        """
        Call the pipeline with the given data.

        Args:
            pipe: The pipeline to be called.
            data: The evaluation data.

        Returns:
            The evaluation results and performance metrics.
        """
        start_time = time.perf_counter()
        pipe_outputs = await tqdm.gather(*[pipe(data) for data in dataset], desc="Evaluation")
        end_time = time.perf_counter()
        return pipe_outputs, self._compute_time_perf(start_time, end_time, len(pipe_outputs))

    def _results_processor(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Process the results.

        Args:
            results: The evaluation results.

        Returns:
            The processed results.
        """
        return {"results": [asdict(result) for result in results]}

    def _compute_metrics(self, metrics: MetricSet, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Compute a metric using the given inputs.

        Args:
            metrics: The metrics to be computed.
            results: The evaluation results.

        Returns:
            The computed metric.
        """
        return {"metrics": metrics.compute(results)}

    def _compute_time_perf(self, start_time: float, end_time: float, num_samples: int) -> Dict[str, Any]:
        """
        Compute the performance metrics.

        Args:
            start_time: The start time.
            end_time: The end time.
            num_samples: The number of samples.

        Returns:
            The performance metrics.
        """
        latency = end_time - start_time
        throughput = num_samples / latency
        latency_sample = 1.0 / throughput

        return {
            "time_perf": {
                "total_time_in_seconds": latency,
                "samples_per_second": throughput,
                "latency_in_seconds": latency_sample,
            },
        }
