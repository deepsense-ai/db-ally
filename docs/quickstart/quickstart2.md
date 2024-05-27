# Quickstart: Semantic Similarity

This guide is a continuation of the [Intro](./index.md) guide. It assumes that you have already set up the views and the collection. If not, please refer to the complete Part 1 code here: [quickstart_code.py](quickstart_code.py).

This guide will demonstrate how to use semantic similarity to handle queries in which the filter values are similar to those in the database, without requiring an exact match. We will use filtering by country as an example.

We will cover the following topics:

- [Understanding the Problem](#the-problem)
- [Installing the Dependencies](#installing-the-dependencies)
- [Defining the Similarity Index](#defining-the-similarity-index)
- [Updating the Similarity Index](#updating-the-similarity-index)
- [Annotating the Filter to Use the Similarity Index](#annotating-the-filter-to-use-the-similarity-index)

!!! note
    This guide uses semantic embeddings from OpenAI and the `faiss` library from Meta for fast similarity search. You can also define custom similarity indexes based on other arbitrary methods of finding similar string values.

## The Problem
First, let's illustrate the problem by using a country name that is not in the database. Change the line containing the question in the `main` function to:

```python
result = await collection.ask("Find someone from the United States with more than 2 years of experience.")
```

When you run the code, you will see that the query returns no candidates. This is because there are no candidates with "United States" as their country name in the database. However, there are candidates with "USA" as the value - but currently, the filter requires an exact match.

We can solve this by using semantic similarity to find the most similar country name to the one given.

## Installing the Dependencies
In addition to the dependencies from Part 1, you will need to install the faiss extension:

```bash
pip install dbally[faiss]
```

## Defining the Similarity Index
A [similarity index](../concepts/similarity_indexes.md) is an object that, given a value, returns the most similar string from a pre-defined list. In this example, it will hold the country names used in the database and return the most similar country name to the one given in the question.

A similarity index typically consists of two parts:

- A fetcher: an object that retrieves the candidate values (in our case: country names from the database).
- A store: an object that stores the candidate values and can be used to find the most similar values to a given value.

First, let's define a fetcher that will fetch the country names from the database (add this before the `CandidateView` class definition):

```python
from dbally.similarity import SimpleSqlAlchemyFetcher

country_fetcher = SimpleSqlAlchemyFetcher(
    engine,
    table=Candidate,
    column=Candidate.country,
)
```

!!! note
    The `SimpleSqlAlchemyFetcher` is one of the built-in fetchers that can be used to fetch values from a SqlAlchemy database, but you can also define custom fetchers.

Next, let's define a store that will store the country names and can be used to find the most similar country name to a given value:

```python
from dbally.similarity import FaissStore
from dbally.embeddings.litellm import LiteLLMEmbeddingClient

country_store = FaissStore(
    index_dir="./similarity_indexes",
    index_name="country_similarity",
    embedding_client=LiteLLMEmbeddingClient(
        model="text-embedding-3-small",  # to use openai embedding model
        api_key=os.environ["OPENAI_API_KEY"],
    ),
)
```

In this example, we used the `FaissStore` store, which employs the `faiss` library for fast similarity search. We also used the `LiteLLMEmbeddingClient` to get the semantic embeddings for the country names. Replace `your-api-key` with your OpenAI API key.

Finally, let's define the similarity index:

```python
from dbally.similarity import SimilarityIndex

country_similarity = SimilarityIndex(
    fetcher=country_fetcher,
    store=country_store,
)
```

## Updating the Similarity Index
The similarity index needs to be updated with the new values from the database. You can do this by calling the `update` method.

Add the following code at the beginning of the `main` function:

```python
country_similarity.update()
```

!!! note
    The `update` method will re-fetch all possible values from the data source and re-index them. Usually, you wouldn't call this method each time you use the similarity index. Instead, you would update the index periodically or when the data source changes. See the [How-To: Update Similarity Indexes](../how-to/update_similarity_indexes.md) guide for more information.

## Annotating the Filter to Use the Similarity Index
Now that we have the similarity index, we can use it to annotate the filter to use the similarity index when filtering candidates by country:

To do this, replace the previous definition of the `from_country` filter with the following (note the type annotation for the `country` parameter):

```python
from typing import Annotated

@decorators.view_filter()
def from_country(self, country: Annotated[str, country_similarity]) -> sqlalchemy.ColumnElement:
    """
    Filters candidates from a specific country.
    """
    return Candidate.country == country
```

!!! warning
    The `Annotated` type is not available in Python 3.8 and earlier. If you are using an older version of Python, you can install the `typing-extensions` package and use the `Annotated` type from there:

    ```python
    from typing_extensions import Annotated
    ```

Now, when you run a query with the `from_country` filter, the similarity index will be used to automatically find the most similar country name to the one given in the query.

!!! note
    Alternatively, you can use the `SimilarityIndex` object directly, for example in this case:

    ```python
    country = country_similarity.similar("United States")
    ```

## Running the Code
Now, when you run the code again, you will see that the query returns candidates from the "USA", even though the question asked for candidates from the "United States".

<details>
  <summary>The expected output</summary>
```
The generated SQL query is: SELECT candidates.name, candidates.country, candidates.years_of_experience, candidates.position, candidates.university, candidates.skills, candidates.tags, candidates.id
FROM candidates
WHERE candidates.country = 'USA' AND candidates.years_of_experience >= 2

Retrieved 1 candidates:
{'name': 'John Smith', 'country': 'USA', 'years_of_experience': 5, 'position': 'Software Engineer', 'university': 'Stanford University', 'skills': 'Java;Python;SQL', 'tags': 'Programming;Team Player', 'id': 1}
```
</details>

That's it! You can apply similar techniques to any other filter that takes a string value.

To see the full example, you can find the code here: [quickstart2_code.py](quickstart2_code.py).

## Next Steps

Explore [Quickstart Part 3: Multiple Views](./quickstart3.md) to learn how to run queries with multiple views and display the results based on the view that was used to fetch the data.
