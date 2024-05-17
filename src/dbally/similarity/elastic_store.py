from typing import Dict, List, Optional, Tuple

import numpy as np
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from dbally.embedding_client.base import EmbeddingClient
from dbally.similarity.store import SimilarityStore


class ElasticStore(SimilarityStore):
    """
    The ElasticStore class stores text embeddings using knnSearch.
    """

    def __init__(
        self,
        index_name: str,
        embedding_client: EmbeddingClient,
        host: str,
        http_auth_tuple: Tuple[str, str],
        ca_cert_path: str,
        search_algorith: Optional[Dict] = None,
    ) -> None:
        """
        Initializes the ElasticStore.

        Args:
            index_name: The name of the index.
            embedding_client: The client to use for creating text embeddings.

        """
        super().__init__()
        self.es = AsyncElasticsearch(
            hosts=host,
            http_auth=http_auth_tuple,
            ca_certs=ca_cert_path,
        )
        self.index_name = index_name
        self.embedding_client = embedding_client
        self.indices = []
        self.search_algorithm = search_algorith or {
            "knn": {
                "field": "search_vector",
                "k": 10,
                "num_candidates": 50,
            }
        }

    async def generate_data(self, data):
        """Asynchronously generates and yields documents with embeddings for a list of words.

        This coroutine iterates over a list of strings, fetches their embeddings using an asynchronous client,
        and yields documents formatted for indexing in Elasticsearch. Each document contains the word, and
        its corresponding embedding, reshaped as a flat array.

        Args:
            data (list of str): A list of words for which embeddings are to be generated.

        Yields:
            dict: A dictionary formatted for Elasticsearch indexing, containing:
                - "_index" (str): The name of the Elasticsearch index.
                - "column" (str): The original word.
                - "search_vector" (numpy.ndarray): The embedding vector for the word, as a flat 1D array.
        """
        for word in data:
            embedding = np.array(await self.embedding_client.get_embeddings([word]), dtype=np.float32).reshape(-1)
            yield {"_index": self.index_name, "column": word, "search_vector": embedding}

    async def store(self, data: List[str]) -> None:
        """
        Stores the data in a faiss index on disk.

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

        await self.es.indices.delete(index=self.index_name)
        await self.es.indices.create(index=self.index_name, mappings=mappings)

        await async_bulk(self.es, self.generate_data(data))

    @staticmethod
    def _filter_response(res):
        """Extracts and returns a specific field from the first hit in an Elasticsearch response.

        This function processes a response from an Elasticsearch query to extract a specific nested field ('column')
        from the first element in the list of hits, if any exist. If there are no hits, it returns None.

        Args:
            res (dict): The response dictionary from an Elasticsearch query.

        Returns:
            The value of the 'column' field from the first hit in the response, or None if there are no hits.
        """
        if len(res["hits"]["hits"]) != 0:
            result = res["hits"]["hits"][0]["_source"]["column"]
        else:
            result = None
        return result

    async def find_similar(self, text: str) -> Optional[str]:
        """
        Finds the most similar text in the store or returns None if no similar text is found.

        Args:
            text: The text to find similar to.

        Returns:
            The most similar text or None if no similar text is found.
        """
        embedding = np.array(await self.embedding_client.get_embeddings([text]), dtype=np.float32).reshape(-1)

        for key in self.search_algorithm:
            self.search_algorithm[key]["query_vector"] = embedding
            break

        search_results = await self.es.search(
            **self.search_algorithm,
        )
        result = self._filter_response(search_results)
        return result
