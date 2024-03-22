# Concept: IQL

Intermediate Query Language (IQL) is a simple language that serves as an abstraction layer between natural language and data source-specific query syntax, such as SQL. In db-ally, LLM utilizes IQL to express complex queries in a simplified way.

For instance, an LLM might generate an IQL query like this when asked "Find me French candidates suitable for a senior data scientist position":

```
from_country('France') AND senior_data_scientist_position()
```

The capabilities made available to the AI model via IQL differ between projects. Developers control these by defining [Views](views.md). db-ally automatically exposes special methods defined in views, known as "filters", via IQL. For instance, the expression above suggests that the specific project contains a view that includes the `from_country` and `senior_data_scientist_position` methods (and possibly others that the LLM did not choose to use for this particular question). Additionally, the LLM can use Boolean operators (`and`,`or`, `not`) to combine individual filters into more complex expressions.

IQL is at the heart of db-ally. By providing a layer of abstraction between the LLM and the data source, it significantly contributes to the primary benefits of db-ally: consistency, security, efficiency, and portability. <!-- TOOD: Link to benefits section of README -->
