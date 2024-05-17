from typing import Dict, List, Optional, Tuple

import numpy as np
from elasticsearch import Elasticsearch

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
        self.es = Elasticsearch(
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

        self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, mappings=mappings)

        operations = []
        for word in data:
            payload = {}
            operations.append({"index": {"_index": self.index_name}})
            # Transforming the title into an embedding using the model
            # embedding = self.model.encode(word)
            embedding = np.array(await self.embedding_client.get_embeddings([word]), dtype=np.float32).reshape(-1)
            payload["column"] = word
            payload["search_vector"] = embedding
            operations.append(payload)

        self.es.bulk(index=self.index_name, operations=operations, refresh=True)

    @staticmethod
    def _filter_response(res):
        if len(res["hits"]["hits"]) != 0:
            # result = [hit["_source"]["column"] for hit in res["hits"]["hits"]]
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
        # embedding = self.model.encode(text)
        embedding = np.array(await self.embedding_client.get_embeddings([text]), dtype=np.float32).reshape(-1)

        for key in self.search_algorithm:
            self.search_algorithm[key]["query_vector"] = embedding
            break

        search_results = self.es.search(
            **self.search_algorithm,
        )
        result = self._filter_response(search_results)
        return result
