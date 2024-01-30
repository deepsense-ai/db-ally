from typing import Optional

from dbally.config import config
from dbally.constants import GenerationModelType
from dbally.llm_client.base import LLMClient
from dbally.llm_client.openai_client import OpenAIClient

LLM_CLIENTS = {GenerationModelType.GPT4: OpenAIClient}


def llm_client_factory(generation_model_type: Optional[GenerationModelType] = None) -> LLMClient:
    """
    Return LLM client instance.

    Args:
        generation_model_type: Generation model type.

    Returns:
        Llm client.
    """

    if generation_model_type is None:
        llm_client = LLM_CLIENTS[config.generation_model_type]
    else:
        llm_client = LLM_CLIENTS[generation_model_type]

    return llm_client()
