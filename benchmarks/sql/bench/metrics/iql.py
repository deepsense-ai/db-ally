from abc import ABC
from typing import Any, Dict, List

from ..pipelines import EvaluationResult
from .base import Metric


class AssessingAccuracy(Metric, ABC):
    """
    Assessing accuracy is proportion of correct decisions out of all decisions made.
    """

    prefix: str
    iql: str

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the assessing accuracy.

        Args:
            results: List of evaluation results.

        Returns:
            Assessing accuracy.
        """
        results = [
            result
            for result in results
            if result.reference.iql
            and result.prediction.iql
            and result.reference.view_name
            and result.prediction.view_name
            and getattr(result.reference.iql, self.iql).generated
            and getattr(result.prediction.iql, self.iql).generated
        ]
        return {
            f"DM/{self.prefix}/ACC": (
                sum(
                    (
                        getattr(result.reference.iql, self.iql).source is not None
                        or getattr(result.reference.iql, self.iql).unsupported
                    )
                    == (
                        getattr(result.prediction.iql, self.iql).source is not None
                        or getattr(result.prediction.iql, self.iql).unsupported
                    )
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class FilteringAccuracy(AssessingAccuracy):
    """
    Filtering accuracy is proportion of correct decisions (to filter or not) out of all decisions made.
    """

    prefix: str = "FLT"
    iql: str = "filters"


class AggregationAccuracy(AssessingAccuracy):
    """
    Aggregation accuracy is proportion of correct decisions (to aggregate or not) out of all decisions made.
    """

    prefix: str = "AGG"
    iql: str = "aggregation"


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


class IQLParseability(Metric, ABC):
    """
    IQL filters parseability is proportion of syntactically correct (parseable) IQLs out of all generated IQLs.
    """

    prefix: str
    iql: str

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
            and (getattr(result.reference.iql, self.iql) and getattr(result.prediction.iql, self.iql))
            and (getattr(result.reference.iql, self.iql).source and getattr(result.prediction.iql, self.iql).source)
        ]
        return {
            f"IQL/{self.prefix}/PARSEABILITY": (
                sum(getattr(result.prediction.iql, self.iql).valid for result in results) / len(results)
                if results
                else None
            )
        }


class IQLFiltersParseability(IQLParseability):
    """
    IQL filters parseability is proportion of syntactically correct (parseable) IQLs out of all generated IQLs.
    """

    prefix: str = "FLT"
    iql: str = "filters"


class IQLAggregationParseability(IQLParseability):
    """
    IQL aggregation parseability is proportion of syntactically correct (parseable) IQLs out of all generated IQLs.
    """

    prefix: str = "AGG"
    iql: str = "aggregation"


class IQLCorrectness(Metric, ABC):
    """
    IQL correctness is proportion of IQLs that produce correct results out of all parseable IQLs.
    """

    prefix: str
    iql: str

    def compute(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Computes the IQL correctness.

        Args:
            results: List of evaluation results.

        Returns:
            IQL correctness.
        """
        results = [
            result
            for result in results
            if (result.reference.iql and result.prediction.iql)
            and (
                getattr(result.reference.iql, self.iql).source
                and getattr(result.prediction.iql, self.iql).source
                and getattr(result.prediction.iql, self.iql).valid
            )
        ]
        return {
            f"IQL/{self.prefix}/CORRECTNESS": (
                sum(
                    getattr(result.prediction.iql, self.iql).source == getattr(result.reference.iql, self.iql).source
                    for result in results
                )
                / len(results)
                if results
                else None
            )
        }


class IQLFiltersCorrectness(IQLCorrectness):
    """
    IQL filters correctness is proportion of IQLs that produce correct results out of all parseable IQLs.
    """

    prefix: str = "FLT"
    iql: str = "filters"


class IQLAggregationCorrectness(IQLCorrectness):
    """
    IQL aggregation correctness is proportion of IQLs that produce correct results out of all parseable IQLs.
    """

    prefix: str = "AGG"
    iql: str = "aggregation"
