from .iql import (
    AggregationAssessorCoT,
    AggregationAssessorCoTH,
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
    AggregationAssessorCoTH.__name__: AggregationAssessorCoTH,
}

__all__ = [
    "PROGRAMS",
    "AggregationAssessorPredict",
    "AggregationAssessorCoT",
    "FilteringAssessorPredict",
    "FilteringAssessorCoT",
    "FilteringAssessorCoTH",
    "AggregationAssessorCoTH",
]
