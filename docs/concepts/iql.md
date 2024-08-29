# Concept: IQL

Intermediate Query Language (IQL) is a simple language that serves as an abstraction layer between natural language and data source-specific query syntax, such as SQL. With db-ally's [structured views](structured_views.md), LLM utilizes IQL to express complex queries in a simplified way. IQL allows developers to model operations such as filtering and aggregation on the underlying data.

## Filtering

For instance, an LLM might generate an IQL query like this when asked "Find me French candidates suitable for a senior data scientist position":

```python
from_country("France") AND senior_data_scientist_position()
```

The capabilities made available to the AI model via IQL differ between projects. Developers control these by defining special [views](structured_views.md). db-ally automatically exposes special methods defined in structured views, known as "filters", via IQL. For instance, the expression above suggests that the specific project contains a view that includes the `from_country` and `senior_data_scientist_position` methods (and possibly others that the LLM did not choose to use for this particular question). Additionally, the LLM can use boolean operators (`AND`, `OR`, `NOT`) to combine individual filters into more complex expressions.

## Aggregation

Similar to filtering, developers can define special methods in [structured views](structured_views.md) that perform aggregation. These methods are also exposed to the LLM via IQL. For example, an LLM might generate the following IQL query when asked "What's the average salary for each country?":

```python
average_salary_by_country()
```

The `average_salary_by_country` groups candidates by country and calculates the average salary for each group.

The aggregation IQL call has access to the raw query, so it can perform even more complex aggregations. Like grouping different columns, or applying a custom functions. We can ask db-ally to generate candidates raport with the following IQL query:

```python
candidate_report()
```

In this case, the `candidate_report` method is defined in a structured view, and it performs a series of aggregations and calculations to produce a report with the average salary, number of candiates, and other metrics, by country.

## Operation chaining

Some queries require filtering and aggregation. For example, to calculate the average salary for a data scientist in the US, we first need to filter the data to include only US candidates who are senior specialists, and then calculate the average salary. In this case, db-ally will first generate an IQL query to filter the data, and then another IQL query to calculate the average salary.

```python
from_country("USA") AND senior_data_scientist_position()
```

```python
average_salary()
```

db-ally will execute queries sequentially to build a single query plan to execute on the data source.
