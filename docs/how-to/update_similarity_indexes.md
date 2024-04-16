# How-To: Update Similarity Indexes

The Similarity Index is a feature provided by db-ally that takes user input and maps it to the closest matching value in the data source using a chosen similarity metric. This feature is handy when the user input does not exactly match the data source, such as when the user asks to "list all employees in the IT department," while the database categorizes this group as the "computer department." To learn more about Similarity Indexes, refer to the [Concept: Similarity Indexes](../concepts/similarity_indexes.md) page.

While Similarity Indexes can be used directly, they are usually used with [Views](../concepts/views.md), annotating arguments to filter methods. This technique lets db-ally automatically match user-provided arguments to the most similar value in the data source. You can see an example of using similarity indexes with views on the [Quickstart Part 2: Semantic Similarity](../quickstart/quickstart2.md) page.

Similarity Indexes are designed to index all possible values (e.g., on disk or in a different data store). Consequently, when the data source undergoes changes, the Similarity Index must update to reflect these alterations. This guide will explain different ways to update Similarity Indexes.

You can update the Similarity Index through Python code or via the db-ally CLI. The following sections explain how to update these indexes using both methods:

* [Update Similarity Indexes via the CLI](#update-similarity-indexes-via-the-cli)
* [Update Similarity Indexes via Python Code](#update-similarity-indexes-via-python-code)
    * [Update on a Single Similarity Index](#update-on-a-single-similarity-index)
    * [Update Similarity Indexes from all Views in a Collection](#update-similarity-indexes-from-all-views-in-a-collection)
    * [Detect Similarity Indexes in Views](#detect-similarity-indexes-in-views)

## Update Similarity Indexes via the CLI

To update Similarity Indexes via the CLI, you can use the `dbally update-index` command. This command requires a path to what you wish to update. The path should follow this format: "path.to.module:ViewName.method_name.argument_name" where each part after the colon is optional. The more specific your target is, the fewer Similarity Indexes will be updated.

For example, to update all Similarity Indexes in a module `my_module.views`, use this command:

```bash
dbally update-index my_module.views
```

To update all Similarity Indexes in a specific View, add the name of the View following the module path:

```bash
dbally update-index my_module.views:MyView
```

To update all Similarity Indexes within a specific method of a View, add the method's name after the View name:

```bash
dbally update-index my_module.views:MyView.method_name
```

Lastly, to update all Similarity Indexes in a particular argument of a method, add the argument name after the method name:

```bash
dbally update-index my_module.views:MyView.method_name.argument_name
```

## Update Similarity Indexes via Python Code
### Update on a Single Similarity Index
To manually update a Similarity Index, call the `update` method on the Similarity Index object. The `update` method will re-fetch all possible values from the data source and re-index them. Below is an example of how to manually update a Similarity Index:

```python
from db_ally import SimilarityIndex

# Create a similarity index
similarity_index = SimilarityIndex(fetcher=fetcher, store=store)

# Update the similarity index
await similarity_index.update()
```

### Update Similarity Indexes from all Views in a Collection
If you have a [collection](../concepts/collections.md) and want to update Similarity Indexes in all views, you can use the `update_similarity_indexes` method. This method will update all Similarity Indexes in all views registered with the collection:

```python
from db_ally import create_collection
from db_ally.llm_client.openai_client import OpenAIClient

my_collection = create_collection("collection_name", llm_client=OpenAIClient())

# ... add views to the collection

await my_collection.update_similarity_indexes()
```

!!! info
    Alternatively, for more advanced use cases, you can use Collection's [`get_similarity_indexes`][dbally.Collection.get_similarity_indexes] method to get a list of all Similarity Indexes (allongside the places where they are used) and update them individually.

### Detect Similarity Indexes in Views
If you are using Similarity Indexes to annotate arguments in views, you can use the [`SimilarityIndexDetector`][dbally.similarity.detector.SimilarityIndexDetector] to locate all Similarity Indexes in a view and update them.

For example, to update all Similarity Indexes in a view named `MyView` in a module labeled `my_module.views`, use the following code:

```python
from db_ally import SimilarityIndexDetector

detector = SimilarityIndexDetector.from_path("my_module.views:MyView")
[await index.update() for index in detector.list_indexes()]
```

The `from_path` method constructs a `SimilarityIndexDetector` object from a view path string in the same format as the CLI command. The `list_indexes` method returns a list of Similarity Indexes detected in the view.

For instance, to detect all Similarity Indexes in a module, provide only the path:

```python
detector = SimilarityIndexDetector.from_path("my_module.views")
```

Conversely, to detect all Similarity Indexes in a specific method of a view, provide the method name:

```python
detector = SimilarityIndexDetector.from_path("my_module.views:MyView.method_name")
```

Lastly, to detect all Similarity Indexes in a particular argument of a method, provide the argument name:

```python
detector = SimilarityIndexDetector.from_path("my_module.views:MyView.method_name.argument_name")
```