# Concept: Collections

At its core, a collection groups together multiple [views](views.md). Once you've defined your views, the next step is to register them within a collection. Here's how you might do it:

```python
my_collection = dbally.create_collection("collection_name", llm_client=OpenAIClient())
my_collection.add(ExampleView)
my_collection.add(RecipesView)
```

Sometimes, view classes might need certain arguments when they're instantiated. In these instances, you'll want to register your view with a builder function that takes care of supplying these arguments. For instance, with views that rely on SQLAlchemy, you'll typically need to pass a database engine object like so:

```python
my_collection = dbally.create_collection("collection_name", llm_client=OpenAIClient())
engine = sqlalchemy.create_engine("sqlite://")
my_collection.add(ExampleView, lambda: ExampleView(engine))
my_collection.add(RecipesView, lambda: RecipesView(engine))
```

A collection doesn't just organize views; it's also the interface for submitting natural language queries. Each query is processed by a selected view from the collection, which then fetches the requested information from its data source. For example:

```python
my_collection.ask("Find me Italian recipes for soups")
```

In this scenario, the LLM first determines the most suitable view to address the query, and then that view is used to pull the relevant data.

!!! info
    The result of a query is an [`ExecutionResult`][dbally.data_models.execution_result.ExecutionResult] object, which contains the data fetched by the view. It contains a `results` attribute that holds the actual data, structured as a list of dictionaries. The exact structure of these dictionaries depends on the view that was used to fetch the data, which can be obtained by looking at the `view_name` attribute of the `ExecutionResult` object.

It's possible for projects to feature several collections, each potentially housing a different set of views. Moreover, a single view can be associated with multiple collections, offering versatile usage across various contexts.
