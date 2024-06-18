# How-To: Use custom data sources with db-ally

!!! note
    This is an advanced topic. If you're looking to create a view that retrieves data from an SQL database, please refer to the [SQL Views](sql.md) guide instead.

In this guide, we'll show you how to create [structured views](../../concepts/structured_views.md) that connect to custom data sources. This could be useful if you need to retrieve data from a REST API, a NoSQL database, or any other data source not supported by the built-in base views.

## Intro
Firstly, we will create a custom base view called `FilteredIterableBaseView` that retrieves data from a Python iterable and allows it to be filtered. It forms the base that implements data source-specific logic and lets other views inherit from it in order to define filters for specific use cases (similar to how `SqlAlchemyBaseView` is a base view provided by db-ally).

Then, we will create a view called `CandidatesView` that inherits from `FilteredIterableBaseView` and represents a use case of retrieving a list of job candidates. We will define filters for this view.

<details>
  <summary>Sneak Peek: how the <code>CandidatesView</code> will look</summary>
Here's how we want the <code>CandidatesView</code> to look like at the end of this guide. To achieve this, we will first design the <code>FilteredIterableBaseView</code> in a way that supports this.

```python
class CandidateView(FilteredIterableBaseView):
    def get_data(self) -> Iterable:
        """
        Returns a list of sample candidates to be filtered.
        """
        return [
            Candidate(1, "John Doe", "Data Scientist", 2, "France"),
            Candidate(2, "Jane Doe", "Data Engineer", 3, "France"),
            Candidate(3, "Alice Smith", "Machine Learning Engineer", 4, "Germany"),
            Candidate(4, "Bob Smith", "Data Scientist", 5, "Germany"),
            Candidate(5, "Janka Jankowska", "Data Scientist", 3, "Poland"),
        ]

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> Callable[[Candidate], bool]:
        """
        Filters candidates with at least `years` of experience.
        """
        return lambda x: x.years_of_experience >= years

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> Callable[[Candidate], bool]:
        """
        Filters candidates suitable for a senior data scientist position.
        """
        return lambda x: x.position in ["Data Scientist", "Machine Learning Engineer", "Data Engineer"] and x.years_of_experience >= 3

    @decorators.view_filter()
    def from_country(self, country: str) -> Callable[[Candidate], bool]:
        """
        Filters candidates from a specific country.
        """
        return lambda x: x.country == country
```
</details>

Lastly, we will illustrate how to use the `CandidatesView` like any other view in db-ally. We will create an instance of the view, add it to a collection, and start querying it.

## Types of custom views
There are two main ways to create custom structured views:

* By subclassing the `MethodsBaseView`: This is the most common method. These views expect filters to be defined as class methods and help manage them. All the built-in db-ally views use this method.
* By subclassing the `BaseStructuredView` directly: This is a more low-level method. It makes no assumptions about how filters are defined and managed. This may be useful if you want to create a view that doesn't fit the standard db-ally view pattern, like when the list of available filters is dynamic or comes from an external source. In these cases, you'll need to create the entire filter management logic yourself by implementing the `list_filters` and `apply_filters` methods.

If you're not sure which method to choose, we recommend starting with the `MethodsBaseView`. It's simpler and easier to use, and you can switch to the `BaseStructuredView` later if you find you need more control over filter management. For this guide, we'll focus on the `MethodsBaseView`.

!!! note
    Both are methods of creating [structured views](../../concepts/structured_views.md). If you're looking to create a [freeform view](../../concepts/freeform_views.md), refer to the [Freeform Views](text-to-sql.md) guide instead.

## Example
Throughout the guide, we'll use an example of creating a custom base view called `FilteredIterableBaseView`. To keep things simple, the "data source" it uses is a list defined in Python. The goal is to demonstrate how to create a custom view and define filters for it. In most real-world scenarios, data would usually come from an external source, like a REST API or a database.

Next, we are going to create a view that inherits from `FilteredIterableBaseView` and implements a use case of retrieving a list of job candidates. This is the same use case from the [Quickstart](../../quickstart/index.md) guide - but this time we'll use a custom view instead of the built-in `SqlAlchemyBaseView`. For comparison, you can refer to the Quickstart guide.

Before we start, let's define a simple data class to represent a candidate:

```python
from dataclasses import dataclass

@dataclass
class Candidate:
    id: int
    name: str
    position: str
    years_of_experience: int
    country: str
```

## Creating a custom view
In db-ally, the typical approach is to have a base view that inherits from `MethodsBaseView` and implements elements specific to a type of data source (for example, [`SqlAlchemyBaseView`](sql.md) is a base view provided by db-ally). Subsequently, you can create views that inherit from this base view, reflecting business logic specific to given use cases, including defining the filter methods.

For our example, let's create a base class called `FilteredIterableBaseView`:

```python
from db_ally import MethodsBaseView

class FilteredIterableBaseView(MethodsBaseView):
    """
    A base view that retrieves data from an iterable and allows it to be filtered.
    """
```

For now, this class is empty, but we'll build upon it in the following sections.

## Specifying how filters should be applied
Classes that inherit from `FilteredIterableBaseView` can define filters as methods. The LLM will choose which of these filters to use, feed them with arguments, and determine how to combine them using boolean operators. To achieve this, the LLM uses its own language, [IQL](../../concepts/iql.md). db-ally translates the IQL expressions and passes the parsed IQL tree to your view via the `apply_filters` method. This method is responsible for identifying the selected filter methods and applying them to the data (which could vary based on the data source).

Let's implement the required `apply_filters` method in our `FilteredIterableBaseView`. Additionally, we'll create a helper method, `build_filter_node`, responsible for handling a single node of the IQL tree (either a filter or a logical operator). We'll use recursion to handle these nodes since they can have children (a logical operator can have two children that are filters, for instance).

```python
    def __init__(self) -> None:
        super().__init__()
        self._filter: Callable[[Any], bool] = lambda x: True

    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the selected filters to the view.

        Args:
            filters: IQLQuery object representing the filters to apply
        """
        self._filter = await self.build_filter_node(filters.root)

    async def build_filter_node(self, node: syntax.Node) -> Callable[[Any], bool]:
        """
        Turns a filter node from the IQLQuery into a Python function.

        Args:
            node: IQLQuery node representing the filter or logical operator
        """
        if isinstance(node, syntax.FunctionCall):  # filter
            return await self.call_filter_method(node)
        if isinstance(node, syntax.And):  # logical AND
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return lambda x: all(child(x) for child in children)  # combine children with logical AND
        if isinstance(node, syntax.Or):  # logical OR
            children = await asyncio.gather(*[self.build_filter_node(child) for child in node.children])
            return lambda x: any(child(x) for child in children)  # combine children with logical OR
        if isinstance(node, syntax.Not):  # logical NOT
            child = await self.build_filter_node(node.child)
            return lambda x: not child(x)
        raise ValueError(f"Unsupported grammar: {node}")
```

In the `apply_filters` method, we're calling the `build_filter_node` method on the root of the IQL tree. The `build_filter_node` method uses recursion to create an object that represents the combined logic of the IQL expression and the returned filter methods. For `FilteredIterableBaseView`, this object is a function that takes a single argument (a candidate) and returns a boolean. We save this function in the `_filter` attribute.

The method named `call_filter_method` that we called within `build_filter_node` is provided by the built-in `MethodsBaseView` and is responsible for calling the filter methods defined in the view.

!!! note
    You may ask why the code ensures the support for more than two children for `And` and `Or` nodes. Somewhat surprisingly, such nodes might have an arbitrary number of children. For instance, an IQL expression `filter1() AND filter2()` will result in an `And` node with two children, whereas an expression `filter1() AND filter2() AND filter3()` will lead to an `And` node with three children.

## Specifying how to execute the view
The `FilteredIterableBaseView` will also need to implement the `execute` method. This method retrieves the data from the data source and applies the combined filters. Typically, this method would need to connect to an external data source (like a REST API or a database) and retrieve the data. In this guide, the data is just a simple Python iterable. This will be provided through an abstract method `get_data` that classes inheriting from `FilteredIterableBaseView` will need to implement.

```python
import abc
from typing import Callable, Any, Iterable

from dbally.iql import IQLQuery
from dbally.collection.results import ViewExecutionResult

@abc.abstractmethod
def get_data(self) -> Iterable:
    """
    Returns the full data to be filtered.
    """

def execute(self, dry_run: bool = False) -> ViewExecutionResult:
    filtered_data = list(filter(self._filter, self.get_data()))

    return ViewExecutionResult(results=filtered_data, context={})
```

The `execute` function gets the data (by calling the `get_data` method) and applies the combined filters to it. We're using the [`filter`](https://docs.python.org/3/library/functions.html#filter) function from Python's standard library to accomplish this. The filtered data is then returned as a list.

## Creating a view
Now that `FilteredIterableBaseView` is complete, we can create a view that inherits from it and represents the use case of retrieving a list of job candidates. We'll name this view `CandidatesView`:

```python
from dbally import decorators

class CandidateView(FilteredIterableBaseView):
    def get_data(self) -> Iterable:
        """
        Returns a list of sample candidates to be filtered.
        """
        return [
            Candidate(1, "John Doe", "Data Scientist", 2, "France"),
            Candidate(2, "Jane Doe", "Data Engineer", 3, "France"),
            Candidate(3, "Alice Smith", "Machine Learning Engineer", 4, "Germany"),
            Candidate(4, "Bob Smith", "Data Scientist", 5, "Germany"),
            Candidate(5, "Janka Jankowska", "Data Scientist", 3, "Poland"),
        ]

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> Callable[[Candidate], bool]:
        """
        Filters candidates having at least `years` of experience.
        """
        return lambda x: x.years_of_experience >= years

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> Callable[[Candidate], bool]:
        """
        Filters candidates suitable for a senior data scientist role.
        """
        return lambda x: x.position in ["Data Scientist", "Machine Learning Engineer", "Data Engineer"] and x.years_of_experience >= 3

    @decorators.view_filter()
    def from_country(self, country: str) -> Callable[[Candidate], bool]:
        """
        Filters candidates from a specific country.
        """
        return lambda x: x.country == country
```

In the `CandidatesView`, we implemented `get_data` to return a list of sample `Candidate` instances. Three filter methods are also defined: `at_least_experience`, `senior_data_scientist_position`, and `from_country`. These methods return functions that apply the given filter logic by accepting a `Candidate` object as an argument and returning a boolean value to indicate whether the candidate should be included in the results.

## Using the View
Finally, we can use the `CandidatesView` just like any other view in db-ally. We can create an instance of the view, add it to a collection, and start querying it:

```python
import asyncio
import dbally
from dbally.llms.litellm import LiteLLM

async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("recruitment", llm)
    collection.add(CandidateView)

    result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())
```

When we run the script, we should get this output:

```
Retrieved 1 candidates:
Candidate(id=2, name='Jane Doe', position='Data Engineer', years_of_experience=3, country='France')
```

## Full example
You can access the complete example here: [custom_views_code.py](custom_views_code.py)