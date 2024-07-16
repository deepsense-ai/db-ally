# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
import os
import asyncio
from typing_extensions import Annotated

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
import pandas as pd

import dbally
from dbally import decorators, SqlAlchemyBaseView, DataFrameBaseView, ExecutionResult
from dbally.audit import CLIEventHandler
from dbally.similarity import SimpleSqlAlchemyFetcher, FaissStore, SimilarityIndex
from dbally.embeddings.litellm import LiteLLMEmbeddingClient
from dbally.llms.litellm import LiteLLM

engine = create_engine("sqlite:///examples/recruiting/data/candidates.db")

Base = automap_base()
Base.prepare(autoload_with=engine)

Candidate = Base.classes.candidates


country_similarity = SimilarityIndex(
    fetcher=SimpleSqlAlchemyFetcher(
        engine,
        table=Candidate,
        column=Candidate.country,
    ),
    store=FaissStore(
        index_dir="./similarity_indexes",
        index_name="country_similarity",
        embedding_client=LiteLLMEmbeddingClient(
            model="text-embedding-3-small",  # to use openai embedding model
            api_key=os.environ["OPENAI_API_KEY"],
        ),
    ),
)


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
    def from_country(self, country: Annotated[str, country_similarity]) -> sqlalchemy.ColumnElement:
        """
        Filters candidates from a specific country.
        """
        return Candidate.country == country


jobs_data = pd.DataFrame.from_records(
    [
        {"title": "Data Scientist", "company": "Company A", "location": "New York", "salary": 100000},
        {"title": "Data Engineer", "company": "Company B", "location": "San Francisco", "salary": 120000},
        {"title": "Machine Learning Engineer", "company": "Company C", "location": "Berlin", "salary": 90000},
        {"title": "Data Scientist", "company": "Company D", "location": "London", "salary": 110000},
        {"title": "Data Scientist", "company": "Company E", "location": "Warsaw", "salary": 80000},
    ]
)


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


def display_results(result: ExecutionResult):
    if result.view_name == "CandidateView":
        print(f"{len(result.results)} Candidates:")
        for candidate in result.results:
            print(f"{candidate['name']} - {candidate['skills']}")
    elif result.view_name == "JobView":
        print(f"{len(result.results)} Job Offers:")
        for job in result.results:
            print(f"{job['title']} at {job['company']} in {job['location']}")


async def main():
    dbally.event_handlers = [CLIEventHandler()]
    await country_similarity.update()

    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("recruitment", llm)
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(JobView, lambda: JobView(jobs_data))

    result = await collection.ask("Find me job offers in New York with a salary of at least 100000.")
    display_results(result)

    print()

    result = await collection.ask("Find me candidates from Poland.")
    display_results(result)


if __name__ == "__main__":
    asyncio.run(main())
