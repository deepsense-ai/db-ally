from dspy import InputField, OutputField, Signature


class CheckQuestionFiltering(Signature):
    """
    Given a question, determine whether the answer requires initial data filtering in order to compute it.
    Initial data filtering is a process in which the result set is reduced to only include the rows that
    meet certain criteria specified in the question.
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


class CheckQuestionAggregation(Signature):
    """
    Given a question, determine whether the answer requires data aggregation in order to compute it.
    Data aggregation is a process in which we calculate a single values for a group of rows in the result set.
    """

    question = InputField(
        prefix="Question: ",
    )
    decision = OutputField(
        prefix="Decision: ",
        desc=(
            "indicates whether the answer to the question requires data aggregation. " "(Respond with True or False)"
        ),
    )
