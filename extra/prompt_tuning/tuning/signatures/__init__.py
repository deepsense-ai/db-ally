from .iql import (
    AggregationAssessor,
    AggregationAssessorBaseline,
    AggregationAssessorOptimized,
    FilteringAssessor,
    FilteringAssessorBaseline,
    FilteringAssessorOptimized,
)

SIGNATURES = {
    AggregationAssessorBaseline.__name__: AggregationAssessorBaseline,
    AggregationAssessorOptimized.__name__: AggregationAssessorOptimized,
    FilteringAssessorBaseline.__name__: FilteringAssessorBaseline,
    FilteringAssessorOptimized.__name__: FilteringAssessorOptimized,
}


__all__ = [
    "AggregationAssessor",
    "FilteringAssessor",
    "AggregationAssessorBaseline",
    "AggregationAssessorOptimized",
    "FilteringAssessorBaseline",
    "FilteringAssessorOptimized",
    "SIGNATURES",
]
