from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Union

from sqlalchemy.engine import RowMapping


@dataclass
class AnswerMetadata:
    """Class for storing metadata associated with answer."""

    execution_time: Optional[float] = None


@dataclass
class Answer:
    """Class representing db-ally answer."""

    sql: str
    rows: Union[Sequence[RowMapping], List[Dict]]
    metadata: Optional[AnswerMetadata] = None
    content: Optional[str] = None
