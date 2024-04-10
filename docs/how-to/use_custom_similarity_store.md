# How-To: Store Similarity Index in a Custom Store

[The similarity index](../concepts/similarity_indexes.md) is a feature provided by db-ally designed to map user input to the closest matching value in a data source. In this guide, we will show you how to save this similarity index in a custom store, such as your preferred vector database.

## How a Similarity Index Works

A similarity index is built up of two core components:

* A **fetcher** retrieves all potential values from a data source
* A **store** indexes these values, enabling the system to find the closest match to the user's input

To use a similarity index with a custom store, you need to create a custom store that indexes the values and lets the system find the closest match to the user's input.

## Implementing a Custom Store

To implement a custom store, you need to create a class which extends the `AbstractStore` class provided by db-ally. The `AbstractStore` class has two asynchronous methods that you need to implement:

* `store`: This method should store the values in the custom store.
* `find_similar`: This method should find the value most similar to a given input.

To use a trivial example, let's say you want to store the values in a Python pickle file and find the most similar value using Levenshtein distance. You can create a store like this:

```python
from dbally.similarity.store import AbstractStore
import pickle
import Levenshtein

class PickleStore(AbstractStore):
    def __init__(self, file_path):
        self.file_path = file_path

    async def store(self, values):
        with open(self.file_path, 'wb') as f:
            pickle.dump(values, f)

    async def find_similar(self, value):
        with open(self.file_path, 'rb') as f:
            values = pickle.load(f)
            return min(values, key=lambda x: Levenshtein.distance(x, value))
```

You can then use this store to create a similarity index that maps user input to the closest matching value.

## Using the Custom Store with a Similarity Index

Once you have implemented your custom store, you can use it to create a similarity index. Here's an example of how you can do that using the `PickleStore` class:

```python
from dbally.similarity.index import SimilarityIndex

country_similarity = SimilarityIndex(
    fetcher=DogBreedsFetcher(),
    store=PickleStore(
        file_path="./dog_breeds.pkl",
    )
)
```

In this example, we used the sample `DogBreedsFetcher` fetcher detailed in the [custom fetcher guide](./use_custom_similarity_fetcher.md) and the `PickleStore` to store the values in a Python pickle file. You can use a different fetcher depending on your needs, for example [the Sqlalchemy one described in the Quickstart guide](../quickstart/quickstart2.md)).

## Using the Similarity Index

You can use an index with a custom store [the same way](../quickstart/quickstart2.md) you would use one with a built-in store. The similarity index will map user input to the closest matching value from your data source, enabling you to deliver more accurate responses. It's important to regularly update the similarity index with new values from your data source to keep it current. Do this by invoking the `update` method on the similarity index.

```python
await country_similarity.update()
```

!!! note
    The `update` method will re-fetch all possible values from the data source and re-index them. Usually, you wouldn't call this method each time you use the similarity index. Instead, you would update the index periodically or when the data source changes. See the [How-To: Update Similarity Indexes](../how-to/update_similarity_indexes.md) guide for more information.

Then, you can utilize the similarity index to find the closest matching value to a user input and generate a response based on that value.

```python
print(await country_similarity.similar("bagle"))
```

This will return the closest matching dog breed to "bagle" - in this case, "beagle".

Typically, instead of directly invoking the similarity index, you would employ it to annotate arguments to views, as demonstrated in the [Quickstart guide](../quickstart/quickstart2.md).