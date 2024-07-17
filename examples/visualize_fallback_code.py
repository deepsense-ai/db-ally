# pylint: disable=missing-function-docstring
import asyncio

from recruiting import candidate_view_with_similarity_store, candidates_freeform
from recruiting.candidate_view_with_similarity_store import CandidateView
from recruiting.candidates_freeform import CandidateFreeformView
from recruiting.cypher_text2sql_view import SampleText2SQLViewCyphers, create_freeform_memory_engine
from recruiting.db import ENGINE as recruiting_engine
from recruiting.views import RecruitmentView

import dbally
from dbally.audit import CLIEventHandler, OtelEventHandler
from dbally.gradio import create_gradio_interface
from dbally.llms.litellm import LiteLLM


async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    user_collection = dbally.create_collection("candidates", llm)
    user_collection.add(CandidateView, lambda: CandidateView(candidate_view_with_similarity_store.engine))
    user_collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))

    fallback_collection = dbally.create_collection("freeform candidates", llm, event_handlers=[OtelEventHandler()])
    fallback_collection.add(CandidateFreeformView, lambda: CandidateFreeformView(candidates_freeform.engine))

    second_fallback_collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler()])
    second_fallback_collection.add(RecruitmentView, lambda: RecruitmentView(recruiting_engine))

    user_collection.set_fallback(fallback_collection).set_fallback(second_fallback_collection)

    gradio_interface = await create_gradio_interface(user_collection=user_collection)
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
