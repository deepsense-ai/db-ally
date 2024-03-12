# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
import dbally
import os
import asyncio
from dbally import decorators, SqlAlchemyBaseView

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

engine = create_engine('sqlite:///data/candidates.db')

Base = automap_base()
Base.prepare(autoload_with=engine)

Candidate = Base.classes.candidates

dbally.use_openai_llm(openai_api_key=os.environ["OPENAI_API_KEY"])

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

async def main():
    collection = dbally.create_collection("recruitment")
    collection.add(CandidateView, lambda: CandidateView(engine))

    result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

    print(f"The generated SQL query is: {result.context.get('sql')}")
    print()
    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())
