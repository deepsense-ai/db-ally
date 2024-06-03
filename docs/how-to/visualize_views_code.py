import asyncio
import dotenv
import os

import sqlalchemy

import dbally
from dbally.audit import CLIEventHandler
from dbally.embeddings import LiteLLMEmbeddingClient
from dbally.similarity import SimilarityIndex, SimpleSqlAlchemyFetcher, FaissStore
from dbally.llms.litellm import LiteLLM
from dbally.utils.gradio_adapter import GradioAdapter
from examples.freeform import MyText2SqlView
from sandbox.quickstart2 import CandidateView, engine, Candidate

dotenv.load_dotenv()
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
            api_key=os.environ["OPENAI_API_KEY"],
        ),
    ),
)

freeFormEngine = sqlalchemy.create_engine("sqlite:///:memory:")


async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")

    with freeFormEngine.connect() as connection:
        for table_config in MyText2SqlView(engine).get_tables():
            connection.execute(sqlalchemy.text(table_config.ddl))

    collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(MyText2SqlView, lambda: MyText2SqlView(engine))
    gradio_adapter = GradioAdapter(similarity_store=country_similarity, engine=engine)
    gradio_interface = await gradio_adapter.create_interface(collection)
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
