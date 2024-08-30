from .iql import (
    AggregationAssessorCoT,
    AggregationAssessorPredict,
    FilteringAssessorCoT,
    FilteringAssessorCoTH,
    FilteringAssessorPredict,
)

PROGRAMS = {
    FilteringAssessorPredict.__name__: FilteringAssessorPredict,
    FilteringAssessorCoT.__name__: FilteringAssessorCoT,
    FilteringAssessorCoTH.__name__: FilteringAssessorCoTH,
    AggregationAssessorPredict.__name__: AggregationAssessorPredict,
    AggregationAssessorCoT.__name__: AggregationAssessorCoT,
}

__all__ = [
    "PROGRAMS",
    "AggregationAssessorPredict",
    "AggregationAssessorCoT",
    "FilteringAssessorPredict",
    "FilteringAssessorCoT",
    "FilteringAssessorCoTH",
]
