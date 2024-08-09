from .iql import FilteringAssessorBaseline, FilteringAssessorCoT

PROGRAMS = {
    FilteringAssessorBaseline.__name__: FilteringAssessorBaseline,
    FilteringAssessorCoT.__name__: FilteringAssessorCoT,
}

__all__ = ["PROGRAMS", "FilteringAssessorBaseline", "FilteringAssessorCoT"]
