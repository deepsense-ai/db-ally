from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from omegaconf import DictConfig
from typing_extensions import Self

from ..pipelines import EvaluationResult


class Metric(ABC):
    """
    Base class for metrics.
    """

    def __init__(self, config: Optional[DictConfig] = None) -> None:
        """
        Initializes the metric.

        Args:
            config: The metric configuration.
        """
        self.config = config or {}

    @abstractmethod
    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
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

    def __init__(self, *metrics: Type[Metric]) -> None:
        """
        Initializes the metric set.

        Args:
            metrics: The metrics.
        """
        self._metrics = metrics
        self.metrics: List[Metric] = []

    def __call__(self, config: DictConfig) -> Self:
        """
        Initializes the metrics.

        Args:
            config: The configuration for the metrics.

        Returns:
            The initialized metric set.
        """
        self.metrics = [metric(config) for metric in self._metrics]
        return self

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Compute the metrics.

        Args:
            results: The evaluation results.

        Returns:
            The computed metrics.
        """
        return {name: value for metric in self.metrics for name, value in metric.compute(results).items()}
