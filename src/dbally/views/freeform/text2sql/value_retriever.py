from dataclasses import dataclass
from typing import List

import sqlalchemy


@dataclass
class RetrievedValue:
    """This class represents a value retrieved from the database."""

    table: str
    column: str


class ValueRetriever:
    """This class is responsible for retrieving values from the database that match the user query"""

    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        # Here we need to retrieve all values and create index using BM25 method and apache Lucene
        pass

    def retrieve_values(self, query: str) -> List[RetrievedValue]:
        """It performs coarse-fine search to retrieve values from the database that match the user query

        Args:
            query: _description_

        Returns:
            _description_
        """
        # Use Apache Lucene to perform coarse-grained search

        # Next use LCS to perform fine-grained search
