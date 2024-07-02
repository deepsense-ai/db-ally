# pylint: disable=missing-function-docstring
import asyncio

from recruiting import candidate_view_with_similarity_store, candidates_freeform
from recruiting.candidate_view_with_similarity_store import CandidateView
from recruiting.candidates_freeform import CandidateFreeformView
from recruiting.cypher_text2sql_view import SampleText2SQLViewCyphers, create_freeform_memory_engine

import dbally
from dbally.gradio import create_gradio_interface
from dbally.llms.litellm import LiteLLM


async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection1 = dbally.create_collection("candidates", llm)
    collection2 = dbally.create_collection("freeform candidates", llm)
    collection1.add(CandidateView, lambda: CandidateView(candidate_view_with_similarity_store.engine))
    collection1.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
    collection2.add(CandidateFreeformView, lambda: CandidateFreeformView(candidates_freeform.engine))
    collection1.set_fallback(collection2)
    gradio_interface = await create_gradio_interface(user_collection=collection1)
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
