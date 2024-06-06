# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
import os
import asyncio
from typing_extensions import Annotated

import asyncclick as click
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

import dbally
from dbally import decorators, SqlAlchemyBaseView
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llms.litellm import LiteLLM
from dbally.similarity import SimpleSqlAlchemyFetcher, SimilarityIndex
from dbally.similarity.elastic_vector_search import ElasticVectorStore

load_dotenv()
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
    store=ElasticVectorStore(
        index_name="country_vector_similarity",
        host=os.environ["ELASTIC_STORE_CONNECTION_STRING"],
        ca_cert_path=os.environ["ELASTIC_CERT_PATH"],
        http_user=os.environ["ELASTIC_AUTH_USER"],
        http_password=os.environ["ELASTIC_USER_PASSWORD"],
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


@click.command()
@click.argument("country", type=str, default="United States")
@click.argument("years_of_experience", type=str, default="2")
async def main(country="United States", years_of_experience="2"):
    await country_similarity.update()

    llm = LiteLLM(model_name="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])
    collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(engine))

    result = await collection.ask(
        f"Find someone from the {country} with more than {years_of_experience} years of experience."
    )

    print(f"The generated SQL query is: {result.context.get('sql')}")
    print()
    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())
