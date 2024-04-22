# How-To: Use Chromadb to Store Similarity Index

[ChromadbStore][dbally.similarity.ChromadbStore] allows to use [Chroma vector database](https://docs.trychroma.com/api-reference#methods-on-collection) as a store inside the [SimilarityIndex][dbally.similarity.SimilarityIndex]. Thanks to this, given the query "Show my flights to the USA" and "United States" value representing this country in our database. Similarity index will change `get_flights(to="USA")` into `get_flights(to="United States")`


## Prerequisites

To use Chromadb with db-ally you need to install the chromadb extension

```python
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

Next, you can either use [dbally embedding clients][dbally.embedding_client.EmbeddingClient], such as [OpenAiEmbeddingClient][dbally.embedding_client.OpenAiEmbeddingClient]

```python
from dbally.embedding_client import OpenAiEmbeddingClient

embedding_client=OpenAiEmbeddingClient(
        api_key="your-api-key",
    )

```

or [Chromadb embedding functions](https://docs.trychroma.com/embeddings)

```
from chromadb.utils import embedding_functions
embedding_client = embedding_functions.DefaultEmbeddingFunction()
```

to define your [`ChromadbStore`][dbally.similarity.ChromadbStore].

```python
store = ChromadbStore(index_name="myChromaIndex", client=chroma_client, embedding_calculator=embedding_client)
```

After this setup, you can initialize the SimilarityIndex, and use it with your db-ally filters.

```python
from typing import Annotated

country_similarity = SimilarityIndex(store, DummyCountryFetcher())


@decorators.view_filter()
def from_country(self, country: Annotated[str, country_similarity]) -> sqlalchemy.ColumnElement:
    """
    Filters candidates from a specific country.
    """
    return Candidate.country == country
```
