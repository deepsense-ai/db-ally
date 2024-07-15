from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Union

from typing_extensions import Self

from ..pipelines.base import EvaluationResult


class Metric(ABC):
    """
    Base class for metrics.
    """

    name: str = "Metric"

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Initializes the metric.

        Args:
            config: The metric configuration.
        """
        self.config = config or {}

    @abstractmethod
    def compute(self, results: List[EvaluationResult]) -> Union[int, float]:
        """
        Compute the metric.

        Args:
            results: The evaluation results.

        Returns:
            The computed metric.
        """


class MetricSet:
    """
    Represents a set of metrics.
    """

    def __init__(self, *metrics: List[Type[Metric]]) -> None:
        """
        Initializes the metric set.

        Args:
            metrics: The metrics.
        """
        self._metrics = metrics
        self.metrics: List[Metric] = []

    def __call__(self, config: Dict) -> Self:
        self.metrics = [metric(config) for metric in self._metrics]
        return self

    def compute(self, results: List[EvaluationResult]) -> List[Union[int, float]]:
        """
        Compute the metrics.

        Args:
            results: The evaluation results.

        Returns:
            The computed metrics.
        """
        return {metric.name: metric.compute(results) for metric in self.metrics}
