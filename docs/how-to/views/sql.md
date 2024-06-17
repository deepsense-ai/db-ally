# How-To: Use SQL databases with db-ally

db-ally is a Python library that allows you to use natural language to query various data sources, including SQL databases. This guide will show you how to set up a [structured view](../../concepts/structured.md) to query a SQL database using SQLAlchemy. The guide will work with [any database that SQLAlchemy supports](https://docs.sqlalchemy.org/en/20/dialects/), including SQLite, PostgreSQL, MySQL, Oracle, MS-SQL, Firebird, Sybase, and others.

## Views
The majority of the db-ally's codebase is independent of any particular kind of data source. The part that is specific to a data source is the view. A [view](../../concepts/views.md) is a class that defines how to interact with a data source. It contains methods that define how to retrieve data from the data source and how to filter the data in response to natural language queries.

There are several methods for creating a view that connects to a SQL database, including [creating a custom view from scratch](./custom.md). However, in most cases the easiest will be to use the [`SqlAlchemyBaseView`][dbally.SqlAlchemyBaseView] class provided by db-ally. This tutorial is designed to work with [SQLAlchemy](https://www.sqlalchemy.org/), a popular SQL toolkit and Object-Relational Mapping (ORM) library for Python. To define your view, you will need to produce a class that inherits from `SqlAlchemyBaseView`and implement the `get_select` method, which returns a [SQLAlchemy `Select`](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select) object:

```python
from dbally import SqlAlchemyBaseView

class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Create the initial SQLAlchemy select object, defining which columns to select.
        """
        return sqlalchemy.select(Candidate)
```

The returned `Select` object is used to build the query that will be sent to the database. In this example, the `get_select` method returns a `Select` object that selects all columns from the `candidates` table. You can customize the `Select` object to select specific columns, join multiple tables, and so on.

For example, to only select the `name` and `country` columns, you might return a `Select` object defined as `sqlalchemy.select(Candidate.name, Candidate.country)`.

!!! note
    `Candidate` is a SQLAlchemy model that represents the `candidates` table in the database. You need to [define this model using SQLAlchemy's ORM](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html). For instance, you might define it like this:

    ```python
    from sqlalchemy import Column, Integer, String

    class Candidate(Base):
        __tablename__ = 'candidates'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        country = Column(String)
        years_of_experience = Column(Integer)
    ```

    Alternatively, you can use [SQLAlchemy's automap feature](https://docs.sqlalchemy.org/en/20/orm/extensions/automap.html) to automatically generate the model from the database schema. See the [Quickstart](../../quickstart/index.md) for an example of how this is done.

## Filters
In addition to the `get_select` method, you can define filter methods in your view. A filter method is a method that takes some parameters and returns a [SQLAlchemy `ColumnElement` object](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement). This object represents a condition that can be used to filter the data in the database. See the [SQLAlchemy documentation on `where` clauses](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause) for more details - any condition that can be used in a `where` clause can be returned from a filter method.

For example, you might define a filter method to filter candidates by country:

```python
from dbally import decorators

class CandidateView(SqlAlchemyBaseView):
    # ... (get_select method as before)

    @decorators.view_filter()
    def from_country(self, country: str) -> sqlalchemy.ColumnElement:
        """
        Filter candidates from a specific country.
        """
        return Candidate.country == country

    @decorators.view_filter()
    def with_experience(self, years: int) -> sqlalchemy.ColumnElement:
        """
        Filter candidates with at least `years` of experience.
        """
        return Candidate.years_of_experience >= years
```

In this example, the `from_country` filter takes a `country` parameter and returns a condition that filters candidates by country. The `with_experience` filter takes a `years` parameter and returns a condition that filters candidates by the required years of experience. You can define as many filter methods as you need to support the queries you want to handle. The LLM will decide which filters to use and provide arguments to the filters as needed. They will be used to control which table rows to fetch.

## Connecting to the database
You need to connect to the database using SQLAlchemy before you can use your view. To work, views that inherit from `SqlAlchemyBaseView` require a SQLAlchemy engine to be passed to them. See [the SQLAlchemy documentation on engines](https://docs.sqlalchemy.org/en/20/core/engines.html) for information on how to create an engine for your database. Here is an example of how you might create an engine for a SQLite database:

```python
from sqlalchemy import create_engine

engine = create_engine('sqlite:///examples/recruiting/data/candidates.db')
```

## Registering the view
Once you have defined your view and created an engine, you can register the view with db-ally. You do this by creating a collection and adding the view to it:

```python
from dbally.llms.litellm import LiteLLM

my_collection = dbally.create_collection("collection_name", llm=LiteLLM())
my_collection.add(CandidateView, lambda: CandidateView(engine))
```

## Using the view
To ask a natural language query using your view, you call the `ask` method on the collection:

```python
response = await my_collection.ask("Find me candidates from Italy with at least 5 years of experience")
print(response.results)
```

In cases where you have multiple views in a collection, db-ally will use LLM to determine the most suitable view to address the query, and then that view will be used to pull the relevant data.
