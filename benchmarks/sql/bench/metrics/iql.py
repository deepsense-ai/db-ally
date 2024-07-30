from typing import Any, Dict, List

from ..pipelines import EvaluationResult
from .base import Metric


class FilteringAccuracy(Metric):
    """
    Filtering accuracy indicating proportion of questions that were correctly identified as having filters.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the filtering accuracy.

        Args:
            results: List of evaluation results.

        Returns:
            Filtering accuracy.
        """
        results = [result for result in results if result.reference.iql and result.prediction.iql]
        return {
            "DM/FLT/ACC": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    and result.prediction.iql.filters.unsupported == result.reference.iql.filters.unsupported
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class FilteringPrecision(Metric):
    """
    Filtering precision indicating proportion of questions that were identified as having filters correctly.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the filtering precision.

        Args:
            results: List of evaluation results.

        Returns:
            Filtering precision.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (result.prediction.iql.filters.source or result.prediction.iql.filters.unsupported)
        ]
        return {
            "DM/FLT/PRECISION": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    and result.prediction.iql.filters.unsupported == result.reference.iql.filters.unsupported
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class FilteringRecall(Metric):
    """
    Filtering recall indicating proportion of questions that were correctly identified as having filters.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the filtering recall.

        Args:
            results: List of evaluation results.

        Returns:
            Filtering recall.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (result.reference.iql.filters.source or result.reference.iql.filters.unsupported)
        ]
        return {
            "DM/FLT/RECALL": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    and result.prediction.iql.filters.unsupported == result.reference.iql.filters.unsupported
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class IQLFiltersAccuracy(Metric):
    """
    Ratio of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (
                result.reference.iql.filters.source
                or result.reference.iql.filters.unsupported
                and result.prediction.iql.filters.source
                or result.prediction.iql.filters.unsupported
            )
        ]
        return {
            "IQL/FLT/ACC": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class IQLFiltersPrecision(Metric):
    """
    Ratio of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (
                result.reference.iql.filters.source
                or result.reference.iql.filters.unsupported
                and result.prediction.iql.filters.source
            )
        ]
        return {
            "IQL/FLT/PRECISION": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class IQLFiltersRecall(Metric):
    """
    Ratio of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (
                result.reference.iql.filters.source
                and result.prediction.iql.filters.source
                or result.prediction.iql.filters.unsupported
            )
        ]
        return {
            "IQL/FLT/RECALL": (
                sum(
                    isinstance(result.prediction.iql.filters.source, type(result.reference.iql.filters.source))
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class IQLFiltersParseability(Metric):
    """
    Ratio of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (result.reference.iql.filters and result.prediction.iql.filters)
            and (result.reference.iql.filters.source and result.prediction.iql.filters.source)
        ]
        return {
            "IQL/FLT/PARSEABILITY": (
                sum(result.prediction.iql.filters.valid for result in results) / len(results) if results else None
            )
        }


class IQLFiltersCorrectness(Metric):
    """
    Ratio of predicated IQL filters that are identical to the ground truth ones.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the exact match ratio.

        Args:
            results: List of evaluation results.

        Returns:
            Ratio of predicated queries that are identical to the ground truth ones.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (
                result.reference.iql.filters.source
                and result.prediction.iql.filters.source
                and result.prediction.iql.filters.valid
            )
        ]
        return {
            "IQL/FLT/CORRECTNESS": (
                sum(result.prediction.iql.filters.source == result.reference.iql.filters.source for result in results)
                / len(results)
                if results
                else None
            )
        }
