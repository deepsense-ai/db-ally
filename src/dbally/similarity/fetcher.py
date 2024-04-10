import abc
from typing import List


class SimilarityFetcher(metaclass=abc.ABCMeta):
    """
    Base class for all fetchers. Has to be able to fetch the data from a source and return it as a list of strings.
    """

    @abc.abstractmethod
    async def fetch(self) -> List[str]:
        """
        Fetches the data from the source and returns it as a list of strings.

        Returns:
            The fetched data.
        """
