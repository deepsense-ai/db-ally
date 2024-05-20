from hashlib import sha256
from unittest.mock import AsyncMock, Mock

import chromadb
import pytest

from dbally.embeddings import EmbeddingClient
from dbally.similarity import ChromadbStore

DEFAULT_METADATA = {"hnsw:space": "l2"}
TEST_NAME = "test"


@pytest.fixture
def chroma_store_client():
    store = ChromadbStore(index_name=TEST_NAME, chroma_client=Mock(), embedding_function=Mock(spec=EmbeddingClient))
    store.embedding_function.get_embeddings = AsyncMock(return_value="test_embedding")
    return store


@pytest.fixture
def chroma_store_function():
    return ChromadbStore(
        index_name=TEST_NAME, chroma_client=Mock(), embedding_function=Mock(spec=chromadb.EmbeddingFunction)
    )


def test_chroma_get_chroma_collection_embedding_chroma_client(chroma_store_client):
    chroma_store_client._get_chroma_collection()
    chroma_store_client.chroma_client.get_or_create_collection.assert_called_with(
        name=TEST_NAME, metadata=DEFAULT_METADATA
    )


def test_chroma_get_chroma_collection_chroma_embedding_function(chroma_store_function):
    chroma_store_function._get_chroma_collection()
    chroma_store_function.chroma_client.get_or_create_collection.assert_called_with(
        name=TEST_NAME, metadata=DEFAULT_METADATA, embedding_function=chroma_store_function.embedding_function
    )


RETRIEVED = {"distances": [[0.4]], "documents": [["test"]]}


def get_mocked_collection(mock_client_store: Mock):
    mock_collection = Mock()
    mock_collection.query = Mock(return_value=RETRIEVED)

    mock_client_store._get_chroma_collection = Mock(return_value=mock_collection)

    return mock_collection


@pytest.mark.asyncio
async def test_store_embedding_client(chroma_store_client):
    mock_collection = get_mocked_collection(chroma_store_client)

    await chroma_store_client.store(["test"])
    chroma_store_client.embedding_function.get_embeddings.assert_called_with(["test"])
    mock_collection.add.assert_called_with(
        ids=[sha256(b"test").hexdigest()], embeddings="test_embedding", documents=["test"]
    )


@pytest.mark.asyncio
async def test_store_chroma_embedding_function(chroma_store_function):
    mock_collection = get_mocked_collection(chroma_store_function)

    await chroma_store_function.store(["test"])
    mock_collection.add.assert_called_with(ids=[sha256(b"test").hexdigest()], documents=["test"])


@pytest.mark.asyncio
async def test_find_similar_embedding_client(chroma_store_client):
    mock_collection = get_mocked_collection(chroma_store_client)

    result = await chroma_store_client.find_similar("test")

    chroma_store_client.embedding_function.get_embeddings.assert_called_with(["test"])
    mock_collection.query.assert_called_with(query_embeddings="test_embedding", n_results=1)

    assert result == "test"


@pytest.mark.asyncio
async def test_find_similar_chroma_embedding_function(chroma_store_function):
    mock_collection = get_mocked_collection(chroma_store_function)

    result = await chroma_store_function.find_similar("test")

    mock_collection.query.assert_called_with(query_texts=["test"], n_results=1)

    assert result == "test"


def test_return_best_match_max_distance_is_none(chroma_store_client):
    chroma_store_client.max_distance = None
    result = chroma_store_client._return_best_match(RETRIEVED)

    assert result == "test"


def test_return_best_match_max_distance_is_not_acceptable(chroma_store_client):
    chroma_store_client.max_distance = 0.3
    result = chroma_store_client._return_best_match(RETRIEVED)

    assert result is None


def test_return_best_match_max_distance_is_acceptable(chroma_store_client):
    chroma_store_client.max_distance = 0.5
    result = chroma_store_client._return_best_match(RETRIEVED)

    assert result == "test"
