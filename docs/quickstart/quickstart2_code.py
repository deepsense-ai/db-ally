# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
import os
import asyncio
from typing_extensions import Annotated

from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

import dbally
from dbally import decorators, SqlAlchemyBaseView
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.similarity import SimpleSqlAlchemyFetcher, FaissStore, SimilarityIndex
from dbally.embeddings.litellm import LiteLLMEmbeddingClient
from dbally.llms.litellm import LiteLLM

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


async def main():
    dbally.event_handlers = [CLIEventHandler()]
    await country_similarity.update()

    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("recruitment", llm)
    collection.add(CandidateView, lambda: CandidateView(engine))

    result = await collection.ask("Find someone from the United States with more than 2 years of experience.")

    print(f"The generated SQL query is: {result.context.get('sql')}")
    print()
    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())
