from dbally.config import config
from dbally.constants import GenerationModelType
from dbally.llm_client.base import LLMClient
from dbally.llm_client.openai_client import OpenAIClient

LLM_CLIENTS = {GenerationModelType.GPT4: OpenAIClient}


def llm_client_factory() -> LLMClient:
    """
    Return LLM client instance.

    Returns:
        Llm client.
    """

    llm_client = LLM_CLIENTS[config.generation_model_type]

    return llm_client()
