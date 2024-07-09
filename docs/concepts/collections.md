# Concept: Collections

At its core, a collection groups together multiple [views](views.md). Once you've defined your views, the next step is to register them within a collection. Here's how you might do it:

```python
my_collection = dbally.create_collection("collection_name", llm=LiteLLM())
my_collection.add(ExampleView)
my_collection.add(RecipesView)
```

Sometimes, view classes might need certain arguments when they're instantiated. In these instances, you'll want to register your view with a builder function that takes care of supplying these arguments. For instance, with views that rely on SQLAlchemy, you'll typically need to pass a database engine object like so:

```python
my_collection = dbally.create_collection("collection_name", llm=LiteLLM())
engine = sqlalchemy.create_engine("sqlite://")
my_collection.add(ExampleView, lambda: ExampleView(engine))
my_collection.add(RecipesView, lambda: RecipesView(engine))
```

A collection doesn't just organize views; it's also the interface for submitting natural language queries. Each query is processed by a selected view from the collection, which then fetches the requested information from its data source. For example:

```python
my_collection.ask("Find me Italian recipes for soups")
```

In this scenario, the LLM first determines the most suitable view to address the query, and then that view is used to pull the relevant data.

Sometimes, the selected view does not match question (LLM select wrong view) and will raise an error. In such situations, the fallback collections can be used.
This will cause a next view selection, but from the fallback collection.

```python
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    user_collection = dbally.create_collection("candidates", llm)
    user_collection.add(CandidateView, lambda: CandidateView(candidate_view_with_similarity_store.engine))
    user_collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
    user_collection.add(CandidateView, lambda: (candidate_view_with_similarity_store.engine))

    fallback_collection = dbally.create_collection("freeform candidates", llm)
    fallback_collection.add(CandidateFreeformView, lambda: CandidateFreeformView(candidates_freeform.engine))
    user_collection.set_fallback(fallback_collection)
```
The fallback collection process the same question with declared set of views. The fallback collection could be chained.

```python
    second_fallback_collection = dbally.create_collection("recruitment", llm)
    second_fallback_collection.add(RecruitmentView, lambda: RecruitmentView(recruiting_engine))

    fallback_collection.set_fallback(second_fallback_collection)

```




!!! info
    The result of a query is an [`ExecutionResult`][dbally.collection.results.ExecutionResult] object, which contains the data fetched by the view. It contains a `results` attribute that holds the actual data, structured as a list of dictionaries. The exact structure of these dictionaries depends on the view that was used to fetch the data, which can be obtained by looking at the `view_name` attribute of the `ExecutionResult` object.

It's possible for projects to feature several collections, each potentially housing a different set of views. Moreover, a single view can be associated with multiple collections, offering versatile usage across various contexts.
