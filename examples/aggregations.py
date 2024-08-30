# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring, duplicate-code

import asyncio

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

import dbally
from dbally import SqlAlchemyBaseView, decorators
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llms.litellm import LiteLLM

engine = create_engine("sqlite:///examples/recruiting/data/candidates.db")

Base = automap_base()
Base.prepare(autoload_with=engine)

Candidate = Base.classes.candidates


class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(Candidate)

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> sqlalchemy.ColumnElement:
        """
        Filters candidates with at least `years` of experience.
        """
        return Candidate.years_of_experience >= years

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> sqlalchemy.ColumnElement:
        """
        Filters candidates that can be considered for a senior data scientist position.
        """
        return sqlalchemy.and_(
            Candidate.position.in_(["Data Scientist", "Machine Learning Engineer", "Data Engineer"]),
            Candidate.years_of_experience >= 3,
        )

    @decorators.view_filter()
    def from_country(self, country: str) -> sqlalchemy.ColumnElement:
        """
        Filters candidates from a specific country.
        """
        return Candidate.country == country

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
            self.select.with_only_columns(
                sqlalchemy.func.count(Candidate.id).label("number_of_candidates"),
                Candidate.university,
            )
            .group_by(Candidate.university)
            .order_by(sqlalchemy.desc("number_of_candidates"))
            .limit(limit)
        )


async def main() -> None:
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    dbally.event_handlers = [CLIEventHandler()]

    collection = dbally.create_collection("recruitment", llm)
    collection.add(CandidateView, lambda: CandidateView(engine))

    result = await collection.ask("What is the average years of experience of candidates?")

    print(f"The generated SQL query is: {result.context.get('sql')}")
    for row in result.results:
        print(row)


if __name__ == "__main__":
    asyncio.run(main())
