# How-To: Use Pandas DataFrames with db-ally

In this guide, you will learn how to write [structured views](../../concepts/structured_views.md) that use [Pandas](https://pandas.pydata.org/) DataFrames as their data source. You will understand how to define such a view, create filters that operate on the DataFrame, and register it while providing it with the source DataFrame.

The example used in this guide is a DataFrame containing information about candidates. The DataFrame includes columns such as `id`, `name`, `country`, `years_of_experience`. This is the same use case as the one in the [Quickstart](../../quickstart/index.md) and [Custom Views](./custom.md) guides. Please feel free to compare the different approaches.

## Data
Here is an example of a DataFrame containing information about candidates:

```python
import pandas as pd

CANDIDATE_DATA = pd.DataFrame.from_records([
    {"id": 1, "name": "John Doe", "position": "Data Scientist", "years_of_experience": 2, "country": "France"},
    {"id": 2, "name": "Jane Doe", "position": "Data Engineer", "years_of_experience": 3, "country": "France"},
    {"id": 3, "name": "Alice Smith", "position": "Machine Learning Engineer", "years_of_experience": 4, "country": "Germany"},
    {"id": 4, "name": "Bob Smith", "position": "Data Scientist", "years_of_experience": 5, "country": "Germany"},
    {"id": 5, "name": "Janka Jankowska", "position": "Data Scientist", "years_of_experience": 3, "country": "Poland"},
])
```

## View definition
Views operating on Pandas DataFrames are defined by subclassing the `DataFrameBaseView` class:

```python
from dbally import decorators, DataFrameBaseView

class CandidateView(DataFrameBaseView):
    """
    View for retrieving information about candidates.
    """
```

Typically, a view contains one or more filters that operate on the DataFrame. In the case of views inheriting from `DataFrameBaseView`, filters are expected to return a [`Series`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html) object that can be used as a [boolean index](https://pandas.pydata.org/pandas-docs/version/2.1/user_guide/indexing.html#boolean-indexing) for the original DataFrame. In other words, the filter should return a boolean `Series` with the same length as the original DataFrame where `True` values denote rows that should be included in the result and `False` values indicate rows that should be omitted.

Typically, such `Series` are created automatically by using logical operations on the DataFrame columns, such as `==`, `>`, `<`, `&` (for "and"), `|` (for "or"), and `~` (for "not"). For instance, `df.years_of_experience > 5` will return a boolean `Series` with `True` values for rows where the `years_of_experience` column is greater than 5.

As always, the LLM will choose the best filter to apply based on the query it receives and will combine multiple filters if necessary.

Here are two filters that operate on the DataFrame - one filters candidates with at least a certain number of years of experience and another filters candidates from a specific country:

```python
@decorators.view_filter()
def at_least_experience(self, years: int) -> pd.Series:
    """
    Filters candidates with at least `years` of experience.
    """
    return self.df.years_of_experience >= years

@decorators.view_filter()
def from_country(self, country: str) -> pd.Series:
    """
    Filters candidates from a specific country.
    """
    return self.df.country == country
```

As you see the DataFrame object is accessed via the `self.df` attribute. This attribute is automatically set by the `DataFrameBaseView` class and contains the DataFrame provided when the view is registered.

Here is an example of a more advanced filter that filters candidates considered for a senior data scientist position. It uses the `&` operator to combine two conditions:

```python
@decorators.view_filter()
def senior_data_scientist_position(self) -> pd.Series:
    """
    Filters candidates that can be fit for a senior data scientist position.
    """
    return self.df.position.isin(["Data Scientist", "Machine Learning Engineer", "Data Engineer"]) \
        & (self.df.years_of_experience >= 3)
```

## Registering the view
To use the view, you need to create a [Collection](../../concepts/collections.md) and register the view with it. This is done in the same manner as registering other types of views, but you need to provide the view with the DataFrame on which it should operate:

```python
import dbally
from dbally.llms.litellm import LiteLLM

llm = LiteLLM(model_name="gpt-3.5-turbo")
collection = dbally.create_collection("recruitment", llm)
collection.add(CandidateView, lambda: CandidateView(CANDIDATE_DATA))

result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

print(f"Retrieved {len(result.results)} candidates:")
for candidate in result.results:
    print(candidate)
```

This code will return a list of French candidates eligible for a senior data scientist position and display them:

```
Retrieved 1 candidates:
{'id': 2, 'name': 'Jane Doe', 'position': 'Data Engineer', 'years_of_experience': 3, 'country': 'France'}
```

## Full example
You can access the complete example here: [pandas_views_code.py](pandas_views_code.py)
