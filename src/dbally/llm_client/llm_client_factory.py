from dbally.constants import GenerationModel
from dbally.llm_client.base import LLMClient
from dbally.llm_client.openai_client import OpenAIClient

LLM_CLIENTS = {GenerationModel.GPT4: OpenAIClient}


def llm_client_factory(generation_model_type: GenerationModel) -> LLMClient:
    """
    Return LLM client instance.

    Args:
        generation_model_type: Generation model type.

    Returns:
        Llm client.
    """

    llm_client = LLM_CLIENTS[generation_model_type]

    return llm_client()
