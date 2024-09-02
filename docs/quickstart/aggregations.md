# Quickstart: Aggregations

This guide is a continuation of the [Intro](./intro.md) guide. It assumes that you have already set up the views and the collection. If not, please refer to the complete Part 1 code on [GitHub](https://github.com/deepsense-ai/db-ally/blob/main/examples/intro.py){:target="_blank"}.

In this guide, we will add aggregations to our view to calculate general metrics about the candidates.

## View Definition

To add aggregations to our [structured view](../concepts/structured_views.md), we'll define new methods. These methods will allow the LLM model to perform calculations and summarize data across multiple rows. Let's add three aggregation methods to our `CandidateView`:

```python
class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(Candidate)

    @decorators.view_aggregation()
    def average_years_of_experience(self) -> sqlalchemy.Select:
        """
        Calculates the average years of experience of candidates.
        """
        return self.select.with_only_columns(
            sqlalchemy.func.avg(Candidate.years_of_experience).label("average_years_of_experience")
        )

    @decorators.view_aggregation()
    def positions_per_country(self) -> sqlalchemy.Select:
        """
        Returns the number of candidates per position per country.
        """
        return (
            self.select.with_only_columns(
                sqlalchemy.func.count(Candidate.position).label("number_of_positions"),
                Candidate.position,
                Candidate.country,
            )
            .group_by(Candidate.position, Candidate.country)
            .order_by(sqlalchemy.desc("number_of_positions"))
        )

    @decorators.view_aggregation()
    def candidates_per_country(self) -> sqlalchemy.Select:
        """
        Returns the number of candidates per country.
        """
        return (
            self.select.with_only_columns(
                sqlalchemy.func.count(Candidate.id).label("number_of_candidates"),
                Candidate.country,
            )
            .group_by(Candidate.country)
        )
```

By setting up these aggregations, you enable the LLM to calculate metrics about the average years of experience, the number of candidates per position per country, and the top universities based on the number of candidates.

## Query Execution

Having already defined and registered the view with the collection, we can now execute the query:

```python
result = await collection.ask("What is the average years of experience of candidates?")
print(result.results)
```

This will return the average years of experience of candidates.

<details>
  <summary>The expected output</summary>
```
The generated SQL query is: SELECT avg(candidates.years_of_experience) AS average_years_of_experience
FROM candidates

Number of rows: 1
{'average_years_of_experience': 4.98}
```
</details>

Feel free to try other questions like: "What's the distribution of candidates across different positions and countries?" or "How many candidates are from China?".

## Full Example

Access the full example on [GitHub](https://github.com/deepsense-ai/db-ally/blob/main/examples/aggregations.py){:target="_blank"}.

## Next Steps

Explore [Quickstart Part 3: Semantic Similarity](./semantic-similarity.md) to expand on the example and learn about using semantic similarity.
