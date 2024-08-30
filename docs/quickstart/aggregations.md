# Quickstart: Aggregations

This guide is a continuation of the [Intro](./intro.md) guide. It assumes that you have already set up the views and the collection. If not, please refer to the complete Part 1 code on [GitHub](https://github.com/deepsense-ai/db-ally/blob/main/examples/intro.py){:target="_blank"}.

In this guide, we will add aggregations to our view so that we can calculate some general metrics about the candidates.

## View Definition

tbd

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
            self.select
                .with_only_columns(
                    sqlalchemy.func.count(Candidate.position).label("number_of_candidates"),
                    Candidate.position,
                    Candidate.country,
                )
                .group_by(Candidate.position, Candidate.country)
                .order_by(sqlalchemy.desc("number_of_candidates"))
        )

    @decorators.view_aggregation()
    def top_universities(self, limit: int) -> sqlalchemy.Select:
        """
        Returns the top universities by the number of candidates.
        """
        return (
            self.select
                .with_only_columns(
                    sqlalchemy.func.count(Candidate.id).label("number_of_candidates"),
                    Candidate.university,
                )
                .group_by(Candidate.university)
                .order_by(sqlalchemy.desc("number_of_candidates"))
                .limit(limit)
        )
```

## Query Execution

tbd

## Full Example

Access the full example on [GitHub](https://github.com/deepsense-ai/db-ally/blob/main/examples/aggregations.py){:target="_blank"}.

## Next Steps

Explore [Quickstart Part 3: Semantic Similarity](./semantic-similarity.md) to expand on the example and learn about using semantic similarity.
