from typing import List, Literal, Optional, Union

import chromadb

from dbally.embedding_client.base import EmbeddingClient
from dbally.similarity.store import SimilarityStore


class ChromadbStore(SimilarityStore):
    """Class that stores text embeddings using [Chroma](https://docs.trychroma.com/)"""

    def __init__(
        self,
        index_name: str,
        client: chromadb.Client,
        embedding_calculator: Union[EmbeddingClient, chromadb.EmbeddingFunction],
        max_distance: Optional[float] = None,
        distance_method: Literal["l2", "ip", "cosine"] = "l2",
    ):
        super().__init__()
        self.index_name = index_name
        self.client = client
        self.embedding_calculator = embedding_calculator
        self.max_distance = max_distance

        self._metadata = {"hnsw:space": distance_method}

    def _get_collection(self) -> chromadb.Collection:
        """Based on the selected embedding_calculator chooses how to retrieve the collection.
            If collection doesn't exist it creates one.

        Returns:
            chromadb.Collection: Retrieved collection
        """
        if isinstance(self.embedding_calculator, EmbeddingClient):
            return self.client.get_or_create_collection(name=self.index_name, metadata=self._metadata)

        return self.client.get_or_create_collection(
            name=self.index_name, metadata=self._metadata, embedding_function=self.embedding_calculator
        )

    def _return_best_match(self, retrieved: dict) -> Optional[str]:
        """Based on the retrieved data returns the best match or None if no match is found.

        Args:
            retrieved: Retrieved data, with a column first format

        Returns:
            The best match or None if no match is found
        """
        if self.max_distance is None or retrieved["distances"][0][0] <= self.max_distance:
            return retrieved["documents"][0][0]

        return None

    async def store(self, data: List[str]) -> None:
        """
        Fills chroma collection with embeddings of provided string. As the id uses hash value of the string.

        Args:
            data: The data to store.
        """

        # chroma requires an unique id for every document
        ids = [str(hash(x)) for x in data]

        collection = self._get_collection()

        if isinstance(self.embedding_calculator, EmbeddingClient):
            embeddings = await self.embedding_calculator.get_embeddings(data)

            collection.add(ids=ids, embeddings=embeddings, documents=data)
        else:
            collection.add(ids=ids, documents=data)

    async def find_similar(self, text: str) -> Optional[str]:
        """
        Finds the most similar text in the chroma collection or returns None if the most similar text
        has distance bigger than `self.max_distance`.

        Args:
            text: The text to find similar to.

        Returns:
            The most similar text or None if no similar text is found.
        """

        collection = self._get_collection()

        if isinstance(self.embedding_calculator, EmbeddingClient):
            embedding = await self.embedding_calculator.get_embeddings([text])
            retrieved = collection.query(query_embeddings=embedding, n_results=1)
        else:
            retrieved = collection.query(query_texts=[text], n_results=1)

        return self._return_best_match(retrieved)
