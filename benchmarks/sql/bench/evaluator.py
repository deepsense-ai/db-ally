import time
from typing import Any, Callable, Dict, List, Tuple

from datasets import Dataset
from sqlalchemy import create_engine

from .pipelines.base import EvaluationPipeline, EvaluationResult
from .utils import avarage_execution_time, execute_query


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
        pipe: Callable,
        data: Dataset,
        metrics: Dict[str, Callable],
    ) -> Dict[str, Any]:
        """
        Compute the evaluation results for the given pipeline and data.

        Args:
            pipe: The pipeline to be evaluated.
            data: The evaluation data.
            metrics: The metrics to be computed.

        Returns:
            The evaluation results.
        """
        results, perf_results = await self.call_pipeline(pipe, data)
        results = self.results_processor(results)
        metrics = self.compute_metrics(metrics, results["results"])

        result = {}
        result.update(metrics)
        result.update(perf_results)
        result.update(results)
        return result

    async def call_pipeline(
        self, pipe: EvaluationPipeline, data: Dataset
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
        pipe_output = await pipe(data)
        end_time = time.perf_counter()
        return pipe_output, self._compute_time_perf(start_time, end_time, len(pipe_output))

    def results_processor(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Process the results.

        Args:
            results: The evaluation results.

        Returns:
            The processed results.
        """
        for result in results:
            if result.db_url is not None:
                engine = create_engine(result.db_url)
                if result.reference.sql is not None:
                    result.reference.results, _ = execute_query(result.reference.sql, engine)
                    result.reference.execution_time = avarage_execution_time(result.reference.sql, engine, 10)

                if result.prediction.sql is not None:
                    result.prediction.results, _ = execute_query(result.prediction.sql, engine)
                    result.prediction.execution_time = avarage_execution_time(result.prediction.sql, engine, 10)

        return {
            "results": results,
        }

    def compute_metrics(self, metrics: Dict[str, Callable], results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Compute a metric using the given inputs.

        Args:
            metrics: The metrics to be computed.
            results: The evaluation results.

        Returns:
            The computed metric.
        """
        return {"metrics": {metric_name: metric(results) for metric_name, metric in metrics.items()}}

    @staticmethod
    def _compute_time_perf(start_time: float, end_time: float, num_samples: int) -> Dict[str, Any]:
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
            "total_time_in_seconds": latency,
            "samples_per_second": throughput,
            "latency_in_seconds": latency_sample,
        }
