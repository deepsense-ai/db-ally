from hashlib import sha256
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from dbally.similarity.store import SimilarityStore


class ElasticVectorStore(SimilarityStore):
    """
    The Elastic Vector Store class uses the ELSER (Elastic Learned Sparse EncodeR) model on Elasticsearch to
    store and search data.
    """

    def __init__(
        self,
        index_name: str,
        host: str,
        http_user: str,
        http_password: str,
        ca_cert_path: str,
    ) -> None:
        """
        Initializes the Elastic Vector Store.

        Args:
            index_name: The name of the index.
            host: The host address of the Elasticsearch instance.
            http_user: The username used for HTTP authentication.
            http_password: The password used for HTTP authentication.
            ca_cert_path: The path to the CA certificate for SSL/TLS verification.
        """
        super().__init__()
        self.client = AsyncElasticsearch(
            hosts=host,
            http_auth=(http_user, http_password),
            ca_certs=ca_cert_path,
        )
        self.index_name = index_name

    async def store(self, data: List[str]) -> None:
        """
        Stores the given data in an Elasticsearch store.

        Args:
            data: The data to store in the Elasticsearch index.
        """
        mappings = {
            "properties": {
                "column": {
                    "type": "text",
                },
                "column_embedding": {"type": "sparse_vector"},
            }
        }
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(
                index=self.index_name,
                mappings=mappings,
                settings={"index": {"default_pipeline": "elser-ingest-pipeline"}},
            )
        store_data = [
            {
                "_index": self.index_name,
                "_id": sha256(column.encode("utf-8")).hexdigest(),
                "column": column,
            }
            for column in data
        ]
        await async_bulk(self.client, store_data)

    async def find_similar(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Finds the most similar stored text to the given input text.

        This function performs a search in the Elasticsearch index using text expansion to find
        the stored text that is most similar to the provided input text.

        Args:
            text: The input text for which to find a similar stored text.

        Returns:
            The most similar stored text if found, otherwise None.
        """
        response = await self.client.search(
            index=self.index_name,
            size=1,
            query={
                "text_expansion": {
                    "column_embedding": {
                        "model_id": ".elser_model_2",
                        "model_text": text,
                    }
                }
            },
        )

        return response["hits"]["hits"][0]["_source"]["column"] if len(response["hits"]["hits"]) > 0 else None
