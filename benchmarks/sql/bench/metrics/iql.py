from typing import Any, Dict, List

from ..pipelines import EvaluationResult
from .base import Metric


class FilteringAccuracy(Metric):
    """
    Filtering accuracy is proportion of correct decisions (to filter or not) out of all decisions made.
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
    Filtering precision is proportion of correct decisions to filter out of all decisions to filter.
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
    Filtering recall is proportion of correct decisions to filter out of all cases where filtering
    should have been applied.
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
    IQL filters accuracy is proportion of correct IQL generations and unsupported query identifications out
    of all attempts.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL filters accuracy.

        Args:
            results: List of evaluation results.

        Returns:
            IQL filters accuracy.
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
    IQL filters precision is proportion of correct IQL generations out of all IQL generation attempts.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL filters precision.

        Args:
            results: List of evaluation results.

        Returns:
            IQL filters precision.
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
    IQL filters recall is proportion of correct IQL generations out of all cases where an IQL
    should have been generated.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL filters recall.

        Args:
            results: List of evaluation results.

        Returns:
            IQL filters recall.
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
    IQL filters parseability is proportion of syntactically correct (parseable) IQLs out of all generated IQLs.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL filters parseability.

        Args:
            results: List of evaluation results.

        Returns:
            IQl filters parseability.
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
    IQL filters correctness is proportion of IQLs that produce correct results out of all parseable IQLs.
    """

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL filters correctness.

        Args:
            results: List of evaluation results.

        Returns:
            IQL filters correctness.
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
