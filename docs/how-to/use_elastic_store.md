# How-To: Use Elastic to Store Similarity Index

[The similarity index](../concepts/similarity_indexes.md) is a feature provided by db-ally designed to map user input to the closest matching value in a data source. In this guide, we will show you how to execute similarity search by using elastic search.
In the example the elastic search engine is provided by official docker image. 

## Environment setup

* [Download and deploy elastic search docker image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html). Instructions to set up kibana environment are not required.

```commandline
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.13.4
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.13.4
# Copy the generated elastic password and enrollment token. These credentials are only shown when you start Elasticsearch for the first time. You can regenerate the credentials using the following commands.
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
```

* Store specific (docker container creation printed) output to following variables in the project .venv file 
  - ELASTIC_STORE_CONNECTION_STRING (e.g ```https://localhost:9200```),
  - ELASTIC_CERT_PATH (e.g ```/home/username/certs/http_ca.crt```)
  - ELASTIC_AUTH_USER (e.g ```"elastic```)
  - ELASTIC_USER_PASSWORD (e.g ```uazxUIzCHwA7hcN6+7-5```)

* Install elastic search python client
```commandline
pip install elasticsearch==8.13.1
```

## Implementing a SimilarityIndex

To implement a Similarity Index with elastic store create ElasticStore object and pass it to a store argument.
In the following example sensitive data has been loaded from .env file.

```python
load_dotenv()

country_similarity = SimilarityIndex(
    fetcher=SimpleSqlAlchemyFetcher(
        engine,
        table=Candidate,
        column=Candidate.country,
    ),
    store=ElasticStore(
        index_name="country_similarity",
        host=os.environ["ELASTIC_STORE_CONNECTION_STRING"],
        ca_cert_path=os.environ["ELASTIC_CERT_PATH"],
        http_auth_tuple=(os.environ["ELASTIC_AUTH_USER"], os.environ["ELASTIC_USER_PASSWORD"]),
        embedding_client=OpenAiEmbeddingClient(
            api_key=os.environ["OPENAI_API_KEY"],
        ),
    ),
)
```

You can then use this store to create a similarity index that maps user input to the closest matching value.
For example To Search 'Russia' while querying 'RUS' or 'United States` while asking about the USA.

## Links
* [Similarity Indexes](./use_custom_similiarity_store.md)
* [Example](./use_elastic_store_code.py)