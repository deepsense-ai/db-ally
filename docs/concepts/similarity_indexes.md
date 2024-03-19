# Concept: Similarity Indexes

The similarity index is a feature provided by db-ally designed to map a user input to the closest matching value in the data source, using a chosen similarity metric.

For example, a user might ask "list all employees in the IT department," while the database labels this group as the "computer department." The similarity index first catalogs all potential department names, and when a query is made, it identifies the most closely related department name in the database.

A similarity index consists of two main components:

* A **fetcher** that retrieves all possible values from the data source.
* A **store** that indexes these values, allowing the system to find the closest match to the user's input.

The concept of "similarity" is deliberately broad, as it varies depending on the store's implementation to best fit the use case. Db-ally not only supports custom store implementations but also includes various built-in implementations, from simple case-insensitive text matches to more complex embedding-based semantic similarities.

See the [Quickstart Part 2: Semantic Similarity](../quickstart/quickstart2.md) for an example of using a similarity index with a semantic similarity store.
