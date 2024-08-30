from abc import ABC

from dspy import InputField, OutputField, Signature


class FilteringAssessor(Signature, ABC):
    """
    Abstract signature, should be implemented by a concrete signature,
    describing the actual task for the LLM.
    """

    question = InputField(
        prefix="Question: ",
    )
    decision = OutputField(
        prefix="Decision: ",
        desc=(
            "indicates whether the answer to the question requires initial data filtering. "
            "(Respond with True or False)"
        ),
    )


class FilteringAssessorBaseline(FilteringAssessor):
    """
    Given a question, determine whether the answer requires initial data filtering in order to compute it.
    Initial data filtering is a process in which the result set is reduced to only include the rows that
    meet certain criteria specified in the question.
    """


class FilteringAssessorOptimized(FilteringAssessor):
    """
    Given a question, determine whether the answer requires initial data filtering in order to compute it.
    Initial data filtering is a process in which the result set is reduced to only include the rows that
    meet certain criteria specified in the question.
    """


class AggregationAssessor(Signature, ABC):
    """
    Abstract signature, should be implemented by a concrete signature,
    describing the actual task for the LLM.
    """

    question = InputField(
        prefix="Question: ",
    )
    decision = OutputField(
        prefix="Decision: ",
        desc=("indicates whether the answer to the question requires data aggregation. (Respond with True or False)"),
    )


class AggregationAssessorBaseline(AggregationAssessor):
    """
    Given a question, determine whether the answer requires data aggregation in order to compute it.
    Data aggregation is a process in which we calculate a single values for a group of rows in the result set.
    """


class AggregationAssessorOptimized(AggregationAssessor):
    """
    Given a question, determine whether the answer requires data aggregation in order to compute it.
    Data aggregation is a process in which we calculate a single values for a group of rows in the result set.
    """
