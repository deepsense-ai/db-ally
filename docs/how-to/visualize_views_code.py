import asyncio
import dotenv
import os

import sqlalchemy
from sqlalchemy import text

import dbally
from dbally.audit import CLIEventHandler
from dbally.embeddings import LiteLLMEmbeddingClient
from dbally.similarity import SimilarityIndex, SimpleSqlAlchemyFetcher, FaissStore
from dbally.llms.litellm import LiteLLM
from dbally.utils.gradio_adapter import GradioAdapter
from dbally.views.freeform.text2sql import BaseText2SQLView, TableConfig, ColumnConfig
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


class SampleText2SQLViewCyphers(BaseText2SQLView):
    def get_tables(self):
        return [
            TableConfig(
                name="security_specialists",
                columns=[
                    ColumnConfig("id", "SERIAL PRIMARY KEY"),
                    ColumnConfig("name", "VARCHAR(255)"),
                    ColumnConfig("cypher", "VARCHAR(255)"),
                ],
                description="Knowledge base",
            )
        ]


def prepare_freeform_enginge():
    freeform_engine = sqlalchemy.create_engine("sqlite:///:memory:")

    statements = [
        "CREATE TABLE security_specialists (id INTEGER PRIMARY KEY, name TEXT, cypher TEXT)",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Alice', 'HAMAC')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Bob', 'AES')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('Charlie', 'RSA')",
        "INSERT INTO security_specialists (name, cypher) VALUES ('David', 'SHA2')",
    ]

    with freeform_engine.connect() as conn:
        for statement in statements:
            conn.execute(text(statement))

        conn.commit()

    return freeform_engine


async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("new_one", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(prepare_freeform_enginge()))
    gradio_adapter = GradioAdapter()
    gradio_interface = await gradio_adapter.create_interface(collection, similarity_store_list=[country_similarity])
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
