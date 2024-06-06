# pylint: disable=missing-function-docstring
import asyncio

import dbally
from dbally.audit import CLIEventHandler
from dbally.gradio import create_gradio_interface
from dbally.llms.litellm import LiteLLM
from examples.recruting.candidate_view_with_similarity_store import CandidateView, engine
from examples.recruting.cypher_text2sql_view import SampleText2SQLViewCyphers, create_freeform_memory_engine


async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("candidates", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
    gradio_interface = await create_gradio_interface(user_collection=collection)
    if gradio_interface:
        gradio_interface.launch()


if __name__ == "__main__":
    asyncio.run(main())
