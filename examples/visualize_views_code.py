# pylint: disable=missing-function-docstring
import asyncio

from recruiting.candidate_view_with_similarity_store import CandidateView, country_similarity, engine
from recruiting.cypher_text2sql_view import SampleText2SQLViewCyphers, create_freeform_memory_engine

import dbally
from dbally.audit import CLIEventHandler
from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.gradio import create_gradio_interface
from dbally.llms.litellm import LiteLLM


async def main():
    await country_similarity.update()
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    dbally.event_handlers = [CLIEventHandler(), BufferEventHandler()]
    collection = dbally.create_collection("candidates", llm)
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
    gradio_interface = await create_gradio_interface(user_collection=collection)
    gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
