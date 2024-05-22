from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from dbally.embedding_client.base import EmbeddingClient
from dbally.similarity.store import SimilarityStore


class ElasticsearchStore(SimilarityStore):
    """
    The ElasticsearchStore class stores text embeddings and implements method to find the most similar values using
    knn algorithm.
    """

    def __init__(
        self,
        index_name: str,
        embedding_client: EmbeddingClient,
        host: str,
        http_user: str,
        http_password: str,
        ca_cert_path: str,
    ) -> None:
        """
        Initializes the ElasticsearchStore.

        Args:
            index_name (str): The name of the index.
            embedding_client (EmbeddingClient): The client to use for creating text embeddings.
            host (str): The host address of the Elasticsearch instance.
            http_user (str): The username used for HTTP authentication.
            http_password (str): The password used for HTTP authentication.
            ca_cert_path (str): The path to the CA certificate for SSL/TLS verification.
        """
        super().__init__()
        self.client = AsyncElasticsearch(
            hosts=host,
            http_auth=(http_user, http_password),
            ca_certs=ca_cert_path,
        )
        self.index_name = index_name
        self.embedding_client = embedding_client
        self.indices = []

    async def store(self, data: List[str]) -> None:
        """
        Stores the data in a elastic store.

        Args:
            data: The data to store.
        """

        mappings = {
            "properties": {
                "search_vector": {
                    "type": "dense_vector",
                    "index": "true",
                    "similarity": "cosine",
                }
            }
        }

        await self.client.indices.delete(index=self.index_name, ignore_unavailable=True)
        await self.client.indices.create(index=self.index_name, mappings=mappings)
        store_data = [
            {
                "_index": self.index_name,
                "column": word,
                "search_vector": (await self.embedding_client.get_embeddings([word]))[0],
            }
            for word in data
        ]

        await async_bulk(self.client, store_data)

    async def find_similar(
        self,
        text: str,
        k_closest: int = 5,
        num_candidates: int = 50,
    ) -> Optional[str]:
        """
        Finds the most similar text in the store or returns None if no similar text is found.

        Args:
            text: The text to find similar to.
            k_closest: The k nearest neighbours used by knn-search.
            num_candidates: The number of approximate nearest neighbor candidates on each shard.

        Returns:
            The most similar text or None if no similar text is found.
        """
        query_embedding = (await self.embedding_client.get_embeddings([text]))[0]

        search_results = await self.client.search(
            knn={
                "field": "search_vector",
                "k": k_closest,
                "num_candidates": num_candidates,
                "query_vector": query_embedding,
            }
        )

        return (
            search_results["hits"]["hits"][0]["_source"]["column"] if len(search_results["hits"]["hits"]) != 0 else None
        )
