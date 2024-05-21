import time
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, exceptions
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
            index_name (str): The name of the index.
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
        self.indices = []

    async def deploy_elser_mode(self):
        """
        Deploys the ELSER model on ElasticSearch:

        This function performs the following actions:
        - Deletes the existing model `.elser_model_2` if it exists.
        - Creates a new trained model with the specified model ID.
        - Polls the model definition status until the model is fully defined.
        - Starts the deployment of the model with a specified number of allocations.
        - Polls the deployment status until the model deployment is started.
        - Sets up an ingest pipeline using the deployed model.

        """
        try:
            await self.client.ml.delete_trained_model(model_id=".elser_model_2", force=True)
            print("Model deleted successfully, We will proceed with creating one")
        except exceptions.NotFoundError:
            print("Model doesn't exist, but We will proceed with creating one")

        await self.client.ml.put_trained_model(model_id=".elser_model_2", input={"field_names": ["text_field"]})

        while True:
            status = await self.client.ml.get_trained_models(model_id=".elser_model_2", include="definition_status")

            if status["trained_model_configs"][0]["fully_defined"]:
                print("ELSER Model is downloaded and ready to be deployed.")
                break
            print("ELSER Model is downloaded but not ready to be deployed.")
            time.sleep(5)

        await self.client.ml.start_trained_model_deployment(
            model_id=".elser_model_2", number_of_allocations=1, wait_for="starting"
        )

        while True:
            status = await self.client.ml.get_trained_models_stats(
                model_id=".elser_model_2",
            )
            if status["trained_model_stats"][0]["deployment_stats"]["state"] == "started":
                print("ELSER Model has been successfully deployed.")
                break
            print("ELSER Model is currently being deployed.")
            time.sleep(5)

        await self.client.ingest.put_pipeline(
            id="elser-ingest-pipeline",
            description="Ingest pipeline for ELSER",
            processors=[
                {
                    "inference": {
                        "model_id": ".elser_model_2",
                        "input_output": [{"input_field": "column", "output_field": "column_embedding"}],
                    }
                }
            ],
        )

    async def store(self, data: List[str]) -> None:
        """
        Stores the given data in an Elasticsearch store.

        This function performs the following steps:

        1. Deploys the ELSER model by calling `deploy_elser_mode`.
        2. Defines the mappings for the Elasticsearch index.
        3. Deletes the existing index if it exists.
        4. Creates a new index with the specified mappings and settings.
        5. Stores the provided data in the Elasticsearch index using the default ingest pipeline.

        Args:
            data: The data to store in the Elasticsearch index.
        """
        await self.deploy_elser_mode()

        mappings = {
            "properties": {
                "column": {
                    "type": "text",
                },
                "column_embedding": {"type": "sparse_vector"},
            }
        }

        await self.client.indices.delete(index=self.index_name)
        await self.client.indices.create(
            index=self.index_name,
            mappings=mappings,
            settings={"index": {"default_pipeline": "elser-ingest-pipeline"}},
        )
        store_data = [
            {
                "_index": self.index_name,
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
