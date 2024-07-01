# Quickstart: Intro

This guide will help you get started with db-ally. We will use a simple example to demonstrate how to use db-ally to query a database using an AI model. We will use OpenAI's GPT to generate SQL queries based on natural language questions and SqlAlchemy to interact with the database.

!!! note
    For examples of using db-ally with other data sources and AI models, please refer to our other how-to guides.

We will cover the following topics:

- [Installation](#installation)
- [Database Configuration](#configuring-the-database)
- [View Definition](#defining-the-views)
- [OpenAI Access Configuration](#configuring-openai-access)
- [Collection Definition](#defining-the-collection)
- [Query Execution](#running-the-query)

## Installation

To install db-ally, execute the following command:

```bash
pip install dbally
```

Since we will be using OpenAI's GPT, you also need to install the `litellm` extension:

```bash
pip install dbally[litellm]
```

## Database Configuration

In this guide, we will use an example SQLAlchemy database containing a single table named `candidates`. This table includes columns such as `id`, `name`, `country`, `years_of_experience`, `position`, `university`, `skills`, and `tags`. You can download the example database from [candidates.db](https://github.com/deepsense-ai/db-ally/tree/main/examples/recruiting/candidates.db). Alternatively, you can use your own database and models.

To connect to the database using SQLAlchemy, you need an engine and your database models. Start by creating an engine:

```python
from sqlalchemy import create_engine

engine = create_engine('sqlite:///examples/recruiting/data/candidates.db')
```

Next, define an SQLAlchemy model for the `candidates` table. You can either declare the `Candidate` model using [declarative mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#declarative-mapping) or generate it using [automap](https://docs.sqlalchemy.org/en/20/orm/extensions/automap.html). For simplicity, we'll use automap:

```python
from sqlalchemy.ext.automap import automap_base

Base = automap_base()
Base.prepare(autoload_with=engine)
Candidate = Base.classes.candidates
```

## View Definition

To use db-ally, define the views you want to use. A [structured view](../concepts/structured_views.md) is a class that specifies what to select from the database and includes methods that the AI model can use to filter rows. These methods are known as "filters".

```python
from dbally import decorators, SqlAlchemyBaseView
import sqlalchemy

class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Create the initial SQLAlchemy select object, used to build the query.
        """
        return sqlalchemy.select(Candidate)

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> sqlalchemy.ColumnElement:
        """
        Filter candidates with at least `years` of experience.
        """
        return Candidate.years_of_experience >= years

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> sqlalchemy.ColumnElement:
        """
        Filter candidates eligible for a senior data scientist position.
        """
        return sqlalchemy.and_(
            Candidate.position.in_(["Data Scientist", "Machine Learning Engineer", "Data Engineer"]),
            Candidate.years_of_experience >= 3,
        )

    @decorators.view_filter()
    def from_country(self, country: str) -> sqlalchemy.ColumnElement:
        """
        Filter candidates from a specific country.
        """
        return Candidate.country == country
```

By setting up these filters, you enable the LLM to fetch candidates while optionally applying filters based on experience, country, and eligibility for a senior data scientist position.

!!! note
    The `from_country` filter defined above supports only exact matches, which is not always ideal. Thankfully, db-ally comes with a solution for this problem - Similarity Indexes, which can be used to find the most similar value from the ones available. Refer to [Quickstart Part 2: Semantic Similarity](./quickstart2.md) for an example of using semantic similarity when filtering candidates by country.

## OpenAI Access Configuration

To use OpenAI's GPT, configure db-ally and provide your OpenAI API key:

```python
from dbally.llms.litellm import LiteLLM

llm = LiteLLM(model_name="gpt-3.5-turbo", api_key="...")
```

Replace `...` with your OpenAI API key. Alternatively, you can set the `OPENAI_API_KEY` environment variable with your API key and omit the `api_key` parameter altogether.

## Collection Definition

Next, create a db-ally collection. A [collection](../concepts/collections.md) is an object where you register views and execute queries. It also requires an AI model to use for generating [IQL queries](../concepts/iql.md) (in this case, the GPT model defined above).
The collection could have its own event handlers which override the globally defined handlers.

```python
import dbally
from dbally.audit import CLIEventHandler


async def main():
    collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler])
    collection.add(CandidateView, lambda: CandidateView(engine))
```

!!! note
    While this guide uses a single view, you can create multiple views, registering them with the collection. Based on the query, the AI model will determine which view to use.

## Query Execution

Once you have defined and registered the views with the collection, you can run a query. Add the following code to the `main` function:

```python
result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

print(f"The generated SQL query is: {result.context.get('sql')}")
print()
print(f"Retrieved {len(result.results)} candidates:")
for candidate in result.results:
    print(candidate)
```

This code will return a list of French candidates eligible for a senior data scientist position and display them along with the generated SQL query.

To finish, run the `main` function:

```python
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

Now you can run the script and view the results. The database has a single candidate from France who is eligible for a senior data scientist position.

<details>
  <summary>The expected output</summary>
```
The generated SQL query is: SELECT candidates.name, candidates.country, candidates.years_of_experience, candidates.position, candidates.university, candidates.skills, candidates.tags, candidates.id
FROM candidates
WHERE candidates.country = 'France' AND candidates.position IN ('Data Scientist', 'Machine Learning Engineer', 'Data Engineer') AND candidates.years_of_experience >= 3

Retrieved 1 candidates:
{'name': 'Sophie Dubois', 'country': 'France', 'years_of_experience': 4, 'position': 'Data Engineer', 'university': 'École Polytechnique', 'skills': 'SQL;Python;ETL', 'tags': 'Data Warehousing;Big Data', 'id': 46}
```
</details>

## Full Example

Access the full example here: [quickstart_code.py](quickstart_code.py)

## Next Steps

Explore [Quickstart Part 2: Semantic Similarity](./quickstart2.md) to expand on the example and learn about using semantic similarity.