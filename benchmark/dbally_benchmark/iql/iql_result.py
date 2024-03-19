from typing import Optional

from pydantic import BaseModel


class IQLResult(BaseModel):
    """
    Represents a single IQL result.
    """

    question: str
    iql_filters: str
    exception_raised: Optional[bool] = None
