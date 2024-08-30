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
        desc=("indicates whether the answer to the question requires data filtering. " "(Respond with True or False)"),
    )


class FilteringAssessorBaseline(FilteringAssessor):
    """
    Given a question, determine whether the answer requires data filtering in order to compute it.
    Data filtering is a process in which the result set is reduced to only include the rows that
    meet certain criteria specified in the question.
    """


class FilteringAssessorOptimized(FilteringAssessor):
    """
    Given a question, determine whether the answer requires data filtering in order to compute it.
    Data filtering is a process in which the result set is filtered based on the specific features
    stated in the question. Such a question can be easily identified by using words that refer to
    specific feature values (rather than feature names). Look for words indicating specific values
    that the answer should contain.
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
    Most common aggregation functions are counting, averaging, summing, but other types of aggregation are possible.
    """
