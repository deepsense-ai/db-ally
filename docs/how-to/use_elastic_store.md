# How-To: Use Elastic to Store Similarity Index

ElasticStore[https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-store.html] can be used as a store in [SimilarityIndex](../concepts/similarity_indexes.md). In this guide, we will show you how to execute similarity search by using elastic search.
In the example the elastic search engine is provided by official docker image.
There are two approaches available to perform similarity search Elastic Search Store and Elastic Vector Search.
Elastic Search Store uses embeddings and kNN search to find similarities while Elastic Vector Search - semantic search - uses ELSER (Elastic Learned Sparse EncodeR) model
to encode and search the data.

## Environment setup

* [Download and deploy elastic search docker image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

```commandline
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.13.4
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.13.4
# Copy the generated elastic password and enrollment token. These credentials are only shown when you start Elasticsearch for the first time. You can regenerate the credentials using the following commands.
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200

# For vector search it is required to enroll to appropiate subscryption level or trial verison which supports machine learning.
# It is required to download ELSER model for example through kibana
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.13.4
# [Description how to download/enable ELSER model](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)

```

* Install elastic search python client
```commandline
pip install dbally[elasticsearch]
```

## Implementing a SimilarityIndex

To use similarity search it is required to define data fetcher and data store.

### Data fetcher:

```python
class DummyCountryFetcher(SimilarityFetcher):
    async def fetch(self):
        return ["United States", "Canada", "Mexico"]
```

### Data store:
Elastic store similarity search works on embeddings. For create embeddings the embedding client is passed as an argument.
For example, we can use:
* [OpenAiEmbeddingClient][dbally.embedding_client.OpenAiEmbeddingClient].

```python

embeddings=OpenAiEmbeddingClient(api_key="your-api-key")
```

To implement a Similarity Index with elastic store create ElasticStore object and pass it to a store following argument:
* index_name (str): The name of the index/document.
* embedding_client (EmbeddingClient): The client to use for creating text embeddings.
* host (str): The host address of the Elasticsearch instance.
* http_auth_tuple (Tuple[str, str]): A tuple containing the HTTP authentication credentials (username, password).
* ca_cert_path (str): The path to the CA certificate for SSL/TLS verification.

```python

embeddings=OpenAiEmbeddingClient(api_key="your-api-key")

data_store = ElasticsearchStore(
        index_name="country_similarity",
        host="https://localhost:9200",
        ca_cert_path="path_to_cert/http_ca.crt",
        http_username="elastic",
        http_password="password",
        embedding_client=embeddings,
    ),

```

After this setup, you can initialize the SimilarityIndex

```python
country_similarity = SimilarityIndex(
    fetcher=DummyCountryFetcher(),
    store=data_store
)
```

and [update it and find the closest matches in the same way as in built-in similarity indices](./use_custom_similarity_store.md/#using-the-similar

You can then use this store to create a similarity index that maps user input to the closest matching value.
Now you can use this index to map user input to the closest matching value. For example, a user may type 'United States' and our index would return 'USA'.```

## Links
* [Similarity Indexes](./use_custom_similiarity_store.md)
* [Example Elastic Search Store](./use_elasticsearch_store_code.py)
* [Example Elastic Vector Search](./use_elastic_vector_search_code.py)