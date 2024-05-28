# How-To: Update Similarity Indexes

The Similarity Index is a feature provided by db-ally that takes user input and maps it to the closest matching value in the data source using a chosen similarity metric. This feature is handy when the user input does not exactly match the data source, such as when the user asks to "list all employees in the IT department," while the database categorizes this group as the "computer department." To learn more about Similarity Indexes, refer to the [Concept: Similarity Indexes](../concepts/similarity_indexes.md) page.

While Similarity Indexes can be used directly, they are usually used with [Views](../concepts/views.md), annotating arguments to filter methods. This technique lets db-ally automatically match user-provided arguments to the most similar value in the data source. You can see an example of using similarity indexes with views on the [Quickstart Part 2: Semantic Similarity](../quickstart/quickstart2.md) page.

Similarity Indexes are designed to index all possible values (e.g., on disk or in a different data store). Consequently, when the data source undergoes changes, the Similarity Index must update to reflect these alterations. This guide will explain how to update Similarity Indexes in your code.

* [Update a Single Similarity Index](#update-a-single-similarity-index)
* [Update Similarity Indexes from all Views in a Collection](#update-similarity-indexes-from-all-views-in-a-collection)

## Update a Single Similarity Index
To manually update a Similarity Index, call the `update` method on the Similarity Index object. The `update` method will re-fetch all possible values from the data source and re-index them. Below is an example of how to manually update a Similarity Index:

```python
from dbally import SimilarityIndex

# Create a similarity index
similarity_index = SimilarityIndex(fetcher=fetcher, store=store)

# Update the similarity index
await similarity_index.update()
```

## Update Similarity Indexes from all Views in a Collection
If you have a [collection](../concepts/collections.md) and want to update Similarity Indexes in all views, you can use the `update_similarity_indexes` method. This method will update all Similarity Indexes in all views registered with the collection:

```python
from dbally import create_collection
from dbally.llms.litellm import LiteLLM

my_collection = create_collection("my_collection", llm=LiteLLM())

# ... add views to the collection

await my_collection.update_similarity_indexes()
```

!!! info
    Alternatively, for more advanced use cases, you can use Collection's [`get_similarity_indexes`][dbally.Collection.get_similarity_indexes] method to get a list of all Similarity Indexes (allongside the places where they are used) and update them individually.
