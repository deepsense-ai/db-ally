from typing import Optional

from pydantic import BaseModel


class IQLResult(BaseModel):
    """
    Represents a single IQL result.
    """

    question: str
    ground_truth_iql: str
    predicted_iql: str
    exception_raised: Optional[bool] = None
