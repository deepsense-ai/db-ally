from dataclasses import dataclass


@dataclass
class TextToIQLResult:
    """
    Represents a single TextToIQL result.
    """

    question: str
    ground_truth_iql: str
    predicted_iql: str


@dataclass
class TextToSQLResult:
    """
    Represents a single TextToSQL result.
    """

    question: str
    ground_truth_sql: str
    predicted_sql: str
