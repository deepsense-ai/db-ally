from typing import Dict, List

from dbally.exceptions import DbAllyError
from dbally.similarity.index import AbstractSimilarityIndex
from dbally.views.base import IndexLocation


class NoViewFoundError(DbAllyError):
    """
    Error raised when there is no view with the given name.
    """

    def __init__(self, view_name: str) -> None:
        """
        Args:
            view_name: Name of the view that was not found.
        """
        super().__init__(f"No view found with name '{view_name}'.")
        self.view_name = view_name


class IndexUpdateError(DbAllyError):
    """
    Exception for when updating any of the Collection's similarity indexes fails.

    Provides a dictionary mapping failed indexes to their
    respective exceptions as the `failed_indexes` attribute.
    """

    def __init__(
        self,
        failed_indexes: Dict[AbstractSimilarityIndex, Exception],
        failed_locations: List[IndexLocation],
    ) -> None:
        """
        Args:
            failed_indexes: Dictionary mapping failed indexes to their respective exceptions.
            failed_locations: List of locations of failed indexes.
        """
        description = ", ".join(".".join(name for name in location) for location in failed_locations)
        super().__init__(f"Failed to update similarity indexes for {description}.")
        self.failed_indexes = failed_indexes
