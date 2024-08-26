from .iql import AggregationAssessorBaseline, AggregationAssessorCoT, FilteringAssessorBaseline, FilteringAssessorCoT

PROGRAMS = {
    FilteringAssessorBaseline.__name__: FilteringAssessorBaseline,
    FilteringAssessorCoT.__name__: FilteringAssessorCoT,
    AggregationAssessorBaseline.__name__: AggregationAssessorBaseline,
    AggregationAssessorCoT.__name__: AggregationAssessorCoT,
}

__all__ = [
    "PROGRAMS",
    "AggregationAssessorBaseline",
    "AggregationAssessorCoT",
    "FilteringAssessorBaseline",
    "FilteringAssessorCoT",
]
