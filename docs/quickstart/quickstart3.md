# Quickstart: Multiple Views

This guide continues from [Semantic Similarity](./quickstart2.md) guide. It assumes that you have already set up the views and the collection. If not, please refer to the complete Part 2 code here: [quickstart2_code.py](quickstart2_code.py).

The guide illustrates how to use multiple views to handle queries requiring different types of data. `CandidateView` and `JobView` are used as examples.

## How does having multiple views work?

You can register multiple views with a collection. When you run a query, the AI model decides which view to use based on the query. This allows for handling diffrent kinds of queries with different views. Those views can be based on data from the same source (e.g., different tables in the same database), or from different sources (e.g. a database and an API).

Upon selecting the view, the AI model uses it to extract the relevant data from its data source. The query result is an [`ExecutionResult`][dbally.collection.results.ExecutionResult] object. It contains the data extracted by the view, along with other metadata including the name of the view that fetched the data.

## Defining the JobView

Our collection already has a registered `CandidateView` that allows us to extract candidates from the database. Let's now define a `JobView` that can fetch job offers, using a different data source - a Pandas DataFrame.

!!! info
    For further information on utilizing Pandas DataFrames as a data source, refer to the [How-to: How-To: Use Pandas DataFrames with db-ally](../how-to/views/pandas.md) guide.

First, let's define the dataframe that will serve as our data source:

```python
import pandas as pd

jobs_data = pd.DataFrame.from_records([
    {"title": "Data Scientist", "company": "Company A", "location": "New York", "salary": 100000},
    {"title": "Data Engineer", "company": "Company B", "location": "San Francisco", "salary": 120000},
    {"title": "Machine Learning Engineer", "company": "Company C", "location": "Berlin", "salary": 90000},
    {"title": "Data Scientist", "company": "Company D", "location": "London", "salary": 110000},
    {"title": "Data Scientist", "company": "Company E", "location": "Warsaw", "salary": 80000},
])
```

The dataframe holds job offer information, including the job title, company, location, and salary. Let's now define the `JobView` class:

```python
from dbally import decorators, DataFrameBaseView

class JobView(DataFrameBaseView):
    """
    View for retrieving information about job offers.
    """

    @decorators.view_filter()
    def with_salary_at_least(self, salary: int) -> pd.Series:
        """
        Filters job offers with a salary of at least `salary`.
        """
        return self.df.salary >= salary

    @decorators.view_filter()
    def in_location(self, location: str) -> pd.Series:
        """
        Filters job offers in a specific location.
        """
        return self.df.location == location

    @decorators.view_filter()
    def from_company(self, company: str) -> pd.Series:
        """
        Filters job offers from a specific company.
        """
        return self.df.company == company
```

The `JobView` class inherits from `DataFrameBaseView`, a base class for views utilizing Pandas DataFrames as a data source. The class defines three filter methods: `with_salary_at_least`, `in_location`, and `from_company`. These methods filter the job offers based on salary, location, and company, respectively.

!!! note
    The description of the view class is crucial for the AI model to understand the view's purpose. It helps the model decide which view to use for a specific query.

Now, let's register the `JobView` with the collection by adding this line to `main()`:

```python
collection.add(JobView, lambda: JobView(jobs_data))
```

## Running queries with multiple views

Now that we have both `CandidateView` and `JobView` registered with the collection, we can run queries involving both data types. First, let's define a function that can display query results:

```python
from dbally import ExecutionResult

def display_results(result: ExecutionResult):
    if result.view_name == "CandidateView":
        print(f"{len(result.results)} Candidates:")
        for candidate in result.results:
            print(f"{candidate['name']} - {candidate['skills']}")
    elif result.view_name == "JobView":
        print(f"{len(result.results)} Job Offers:")
        for job in result.results:
            print(f"{job['title']} at {job['company']} in {job['location']}")
```

The `display_result` function receives an `ExecutionResult` object as an argument and prints results based on the view that fetched the data. It shows how you can handle different types of data in the query results.

Now, let's try running a query about job offers:

```python
result = await collection.ask("Find me job offers in New York with a salary of at least 100000.")
display_results(result)
```

Based on our data, this should return the following output, provided by the `JobView`:

```
1 Job Offers:
Data Scientist at Company A in New York
```

Now, let's run a candidates query on the same collection:

```python
result = await collection.ask("Find me candidates from Poland")
display_results(result)
```

This query should yield the following output, provided by the `CandidateView`:

```
3 Candidates:
Yuri Kowalski - SQL;Database Management;Data Modeling
Julia Nowak - Adobe XD;Sketch;Figma
Anna Kowalska - AWS;Azure;Google Cloud
```

That wraps it up! You can find the full example code here: [quickstart3_code.py](quickstart3_code.py).

## Next Steps
Visit the [Tutorial](../tutorials.md) for a more comprehensive guide on how to use db-ally.