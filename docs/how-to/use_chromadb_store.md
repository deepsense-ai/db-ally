# How-To: Use Chromadb to Store Similarity Index

[ChromadbStore][dbally.similarity.ChromadbStore] allows to use [Chroma vector database](https://docs.trychroma.com/api-reference#methods-on-collection) as a store inside the [SimilarityIndex][dbally.similarity.SimilarityIndex]. With this feature, when someone searches for 'Show my flights to the USA' and we have 'United States' stored in our database as the country's value, the system will recognize the similarity and convert the query from 'get_flights(to="USA")' to 'get_flights(to="United States")'.


## Prerequisites

To use Chromadb with db-ally you need to install the chromadb extension

```bash
pip install dbally[chromadb]
```

Let's say we have already implemented our [SimilarityFetcher](../how-to/use_custom_similarity_fetcher.md)

```python
class DummyCountryFetcher(SimilarityFetcher):
    async def fetch(self):
        return ["United States", "Canada", "Mexico"]
```

Next, we need to define `Chromadb.Client`. You can [run Chromadb on your local machine](https://docs.trychroma.com/usage-guide#initiating-a-persistent-chroma-client)

```python
import chromadb

chroma_client = chromadb.PersistentClient(path="/path/to/save/to")
```

or [set up Chromadb in the client/server mode](https://docs.trychroma.com/usage-guide#running-chroma-in-clientserver-mode)

```python
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
```

Next, you can either use [one of dbally embedding clients][dbally.embeddings.EmbeddingClient], such as [LiteLLMEmbeddingClient][dbally.embeddings.LiteLLMEmbeddingClient]

```python
from dbally.embeddings.litellm import LiteLLMEmbeddingClient

embedding_client=LiteLLMEmbeddingClient(
    model="text-embedding-3-small",  # to use openai embedding model
    api_key="your-api-key",
)
```

or [Chromadb embedding functions](https://docs.trychroma.com/embeddings)

```python
from chromadb.utils import embedding_functions

embedding_client = embedding_functions.DefaultEmbeddingFunction()
```

to define your [`ChromadbStore`][dbally.similarity.ChromadbStore].

```python
store = ChromadbStore(
    index_name="myChromaIndex",
    chroma_client=chroma_client,
    embedding_function=embedding_client,
)
```

After this setup, you can initialize the SimilarityIndex

```python
from typing import Annotated

country_similarity = SimilarityIndex(store, DummyCountryFetcher())
```

and [update it and find the closest matches in the same way as in built-in similarity indices](./use_custom_similarity_store.md/#using-the-similarity-index) .
