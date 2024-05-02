import json
from abc import ABC, abstractmethod
from typing import List, Set

import sqlalchemy

from dbally.similarity import ChromadbStore, FaissStore


class BaseSelector(ABC):
    """Base class for all other Text2SQL selectors."""

    def __init__(self, n_results) -> None:
        super().__init__()
        self.n_results = n_results

    @abstractmethod
    def get_similar(self, query: str) -> List[str]:
        """It takes the query and return the most similar items stored in this selector.

        Args:
            query: The query to find similar items for.

        Returns:
            _description_
        """


class FromFileSelector(BaseSelector):
    """This selector can be used when we already precalculated the similar items and stored them in a file."""

    def __init__(self, n_results, file_path) -> None:
        super().__init__(n_results)

        with open(file_path, encoding="utf-8") as f:
            self.data = json.load(f)

    def get_similar(self, query: str) -> List[str]:
        """Get the most similar items for the given query.

        Args:
            query: The query to find similar items for.

        Returns:
            List[str]: The most similar items.
        """
        return self.data[query][: self.n_results]


class ColumnSelector(BaseSelector):
    """This selector uses the database to find most similar columns available in the database"""

    def __init__(self, n_results, engine: sqlalchemy.engine.Engine) -> None:
        super().__init__(n_results)
        self.engine = engine


class ChromaColumnSelector(BaseSelector, ChromadbStore):
    """This selector uses the ChromaDB to find most similar columns available in the database"""


class FaissColumnSelector(BaseSelector, FaissStore):
    """This selector uses the Faiss to find most similar columns available in the database"""


class LLMColumnSelector(BaseSelector):
    """This selector uses the LLM to find most similar columns available in the database"""

    def __init__(self, n_results, llm_client) -> None:
        super().__init__(n_results)
        self.llm_client = llm_client


class FewShotSelector(BaseSelector):
    """This finds most similar few-shot examples available in the dataset"""

    def __init__(self, n_results, engine: sqlalchemy.engine.Engine) -> None:
        super().__init__(n_results)
        self.engine = engine

        self._prohibited_values = self._get_prohibited_values()

    def _get_prohibited_values(self) -> Set[str]:
        """Iterate over all tables and columns and get all column names, values etc

        Returns:
            _description_
        """
        # TODO
        return []

    def _prepare_query(self, query: str):
        """This takes a query and anonymizes it

        Args:
            query: _description_

        Returns:
            _description_
        """
        splitted_query = query.split(" ")
        for i, word in enumerate(splitted_query):
            if word in self._prohibited_values:
                splitted_query[i] = "[MASK]"

        return " ".join(splitted_query)

    async def store(self, data: List[str]) -> None:
        """Store the data in the selector

        Args:
            data: _description_
        """
        data = [self._prepare_query(query) for query in data]


class ChromaFewShotSelector(BaseSelector, ChromadbStore):
    """This selector uses the ChromaDB to find most similar few-shot examples available in the dataset"""

    async def find_similar(self, text: str) -> List[str]:
        """Find the most similar few-shot examples for the given query.

        Args:
            text: The query to find similar few-shot examples for.

        Returns:
            List[str]: The most similar few-shot examples.
        """

        results = await self.get_similar(text)

        few_shot = ""
        for question, metadata in results["documents"]:
            few_shot += f"/* Answer the following: {question} */\n"
            few_shot += f"{metadata['sql']}\n"

        return few_shot
