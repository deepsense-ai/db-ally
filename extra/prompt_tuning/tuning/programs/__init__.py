from .iql import AggregationAssessorCoT, AggregationAssessorPredict, FilteringAssessorCoT, FilteringAssessorPredict

PROGRAMS = {
    FilteringAssessorPredict.__name__: FilteringAssessorPredict,
    FilteringAssessorCoT.__name__: FilteringAssessorCoT,
    AggregationAssessorPredict.__name__: AggregationAssessorPredict,
    AggregationAssessorCoT.__name__: AggregationAssessorCoT,
}

__all__ = [
    "PROGRAMS",
    "AggregationAssessorPredict",
    "AggregationAssessorCoT",
    "FilteringAssessorPredict",
    "FilteringAssessorCoT",
]
