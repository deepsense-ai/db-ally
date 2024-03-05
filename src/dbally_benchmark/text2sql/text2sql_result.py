from pydantic import BaseModel


class Text2SQLResult(BaseModel):
    """Class for storing a single instance of Text2SQL evaluation result."""

    db_id: str
    question: str
    ground_truth_sql: str
    predicted_sql: str
