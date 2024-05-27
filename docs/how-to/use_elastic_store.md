# How-To Use Elastic to Store Similarity Index

[ElasticStore](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-store.html) can be used as a store in SimilarityIndex. In this guide, we will show you how to execute a similarity search using Elasticsearch.
In the example, the Elasticsearch engine is provided by the official Docker image. There are two approaches available to perform similarity searches: Elastic Search Store and Elastic Vector Search.
Elastic Search Store uses embeddings and kNN search to find similarities, while Elastic Vector Search, which performs semantic search, uses the ELSER (Elastic Learned Sparse EncodeR) model to encode and search the data.


## Prerequisites

[Download and deploy the Elasticsearch Docker image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html). Please note that for Elastic Vector Search, the Elasticsearch Docker container requires at least 8GB of RAM and
[license activation](https://www.elastic.co/guide/en/kibana/current/managing-licenses.html) to use Machine Learning capabilities.


```commandline
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.13.4
docker run --name es01 --net elastic -p 9200:9200 -it -m 2GB docker.elastic.co/elasticsearch/elasticsearch:8.13.4
```

Copy the generated elastic password and enrollment token. These credentials are only shown when you start Elasticsearch for the first time once. You can regenerate the credentials using the following commands.
```commandline
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
```

To manage elasticsearch engine create Kibana container.
```commandline
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.13.4
```

By default, the Kibana management dashboard is deployed at [link](http://localhost:5601/)


For vector search, it is necessary to enroll in an [appropriate subscription level](https://www.elastic.co/subscriptions) or trial version that supports machine learning.
Additionally, the [ELSER model must be downloaded](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html), which can be done through Kibana. Instructions can be found in the hosted Kibana instance under tabs:
<br />downloading and deploying model - **Analytics -> Machine Learning -> Trained Model**,
<br />vector search configuration - **Search -> Elastic Search -> Vector Search.**


* Install elasticsearch extension
```commandline
pip install dbally[elasticsearch]
```

## Implementing a SimilarityIndex

To use similarity search it is required to define data fetcher and data store.

### Data fetcher

```python
class DummyCountryFetcher(SimilarityFetcher):
    async def fetch(self):
        return ["United States", "Canada", "Mexico"]
```

### Data store
Elastic store similarity search works on embeddings. For create embeddings the embedding client is passed as an argument.
You can use [one of dbally embedding clients][dbally.embeddings.EmbeddingClient], such as [LiteLLMEmbeddingClient][dbally.embeddings.LiteLLMEmbeddingClient].

```python
from dbally.embeddings.litellm import LiteLLMEmbeddingClient

embedding_client=LiteLLMEmbeddingClient(api_key="your-api-key")
```

to define your [`ElasticsearchStore`][dbally.similarity.ElasticsearchStore].

```python
from dbally.similarity.elasticsearch_store import ElasticsearchStore

data_store = ElasticsearchStore(
        index_name="country_similarity",
        host="https://localhost:9200",
        ca_cert_path="path_to_cert/http_ca.crt",
        http_user="elastic",
        http_password="password",
        embedding_client=embedding_client,
    ),

```

After this setup, you can initialize the SimilarityIndex

```python
from dbally.similarity import SimilarityIndex

country_similarity = SimilarityIndex(
    fetcher=DummyCountryFetcher(),
    store=data_store
)
```

and [update it and find the closest matches in the same way as in built-in similarity indices](use_custom_similarity_store.md/#using-the-similar)

You can then use this store to create a similarity index that maps user input to the closest matching value.
To use Elastic Vector search download and deploy [ELSER v2](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#elser-v2) model and create [ingest pipeline](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#elasticsearch-ingest-pipeline).
Now you can use this index to map user input to the closest matching value. For example, a user may type 'United States' and our index would return 'USA'.

## Links
* [Similarity Indexes](use_custom_similarity_store.md)
* [Example Elastic Search Store](use_elasticsearch_store_code.py)
* [Example Elastic Vector Search](use_elastic_vector_store_code.py)