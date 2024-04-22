import chromadb
import pytest
from chromadb import Documents, EmbeddingFunction, Embeddings

from dbally.embedding_client.base import EmbeddingClient
from dbally.similarity import ChromadbStore
from dbally.similarity.fetcher import SimilarityFetcher
from dbally.similarity.index import SimilarityIndex


class DummyCountryFetcher(SimilarityFetcher):
    async def fetch(self):
        return ["United States", "Canada", "Mexico"]


MAPPING = {"United States": [1, 1, 1], "Canada": [-1, -1, -1], "Mexico": [1, 1, -2], "USA": [0.2, 1, 1]}


class DummyEmbeddingClient(EmbeddingClient):
    async def get_embeddings(self, data):
        return [MAPPING[d] for d in data]


class DummyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return [MAPPING[d] for d in input]


@pytest.mark.asyncio
@pytest.mark.parametrize("embedding_calculator", [DummyEmbeddingClient(), DummyEmbeddingFunction()])
async def test_integration_embedding_client(embedding_calculator):
    chroma_client = chromadb.Client()

    store = ChromadbStore(index_name="test", client=chroma_client, embedding_calculator=embedding_calculator)
    fetcher = DummyCountryFetcher()

    index = SimilarityIndex(store, fetcher)

    await index.update()

    assert store._get_collection().count() == 3

    similar = await index.similar("USA")

    assert similar == "United States"
