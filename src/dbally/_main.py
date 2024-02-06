from typing import Optional

from ._collection import Collection
from .iql_generator.iql_generator import IQLGenerator
from .llm_client.base import LLMClient
from .llm_client.openai_client import OpenAIClient
from .view_selection.llm_view_selector import LLMViewSelector

default_llm_client: Optional[LLMClient] = None


def use_openai_llm(model_name: str = "gpt-3.5-turbo", openai_api_key: Optional[str] = None) -> None:
    """
    Set default LLM client to use OpenAI.

    Args:
        model_name: which OpenAI's model should be used
        openai_api_key: OpenAI's API key - if None OPENAI_API_KEY environment variable will be used
    """
    global default_llm_client  # pylint: disable=W0603
    default_llm_client = OpenAIClient(model_name=model_name, api_key=openai_api_key)


def create_collection(name: str) -> Collection:
    """
    Create a new collection that is a container for registering views, configuration and main entrypoint to db-ally
    features.

    Args:
         name: The name of the collection

    Returns:
        a new instance of DBAllyCollection

    Raises:
        ValueError: if default LLM client is not configured
    """
    if not default_llm_client:
        raise ValueError("LLM client is not set.")

    llm_client = default_llm_client
    view_selector = LLMViewSelector(llm_client=llm_client)
    iql_generator = IQLGenerator(llm_client=llm_client)

    return Collection(name, view_selector=view_selector, iql_generator=iql_generator)
