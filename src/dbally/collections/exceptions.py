from typing import Dict

from dbally.exceptions import DbAllyError
from dbally.similarity.index import AbstractSimilarityIndex


class NoViewFoundError(DbAllyError):
    """
    Error raised when there is no view with the given name.
    """


class IndexUpdateError(DbAllyError):
    """
    Exception for when updating any of the Collection's similarity indexes fails.

    Provides a dictionary mapping failed indexes to their
    respective exceptions as the `failed_indexes` attribute.
    """

    def __init__(self, message: str, failed_indexes: Dict[AbstractSimilarityIndex, Exception]) -> None:
        """
        Args:
            failed_indexes: Dictionary mapping failed indexes to their respective exceptions.
        """
        self.failed_indexes = failed_indexes
        super().__init__(message)
