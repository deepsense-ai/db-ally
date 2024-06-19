# pylint: disable=missing-function-docstring
import asyncio

from recruiting import candidate_view_with_similarity_store, candidates_freeform
from recruiting.candidate_view_with_similarity_store import CandidateView, country_similarity
from recruiting.candidates_freeform import CandidateFreeformView
from recruiting.cypher_text2sql_view import SampleText2SQLViewCyphers, create_freeform_memory_engine
from sqlalchemy import create_engine

import dbally
from dbally.audit import CLIEventHandler
from dbally.gradio import create_gradio_interface
from dbally.llms.litellm import LiteLLM

cm_engine = create_engine("postgresql+pg8000://postgres:ikar89pl@localhost:5432/codebase_community")


async def main():
    await country_similarity.update()
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection1 = dbally.create_collection("candidates", llm, event_handlers=[CLIEventHandler()])
    collection2 = dbally.create_collection("freeform candidates", llm, event_handlers=[CLIEventHandler()])
    collection1.add(CandidateView, lambda: CandidateView(candidate_view_with_similarity_store.engine))
    collection1.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
    collection2.add(CandidateFreeformView, lambda: CandidateFreeformView(candidates_freeform.engine))
    multicollection = dbally.create_multicollection("fallback_option", [collection1, collection2])
    gradio_interface = await create_gradio_interface(user_collection=multicollection)
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
