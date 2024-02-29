from typing import List, Optional

from ._collection import Collection
from .audit.event_handlers.base import EventHandler
from .iql_generator.iql_generator import IQLGenerator
from .llm_client.base import LLMClient
from .llm_client.openai_client import OpenAIClient
from .nl_responder.nl_responder import NLResponder
from .view_selection.llm_view_selector import LLMViewSelector

default_llm_client: Optional[LLMClient] = None
default_event_handlers: List[EventHandler] = []


def use_openai_llm(model_name: str = "gpt-3.5-turbo", openai_api_key: Optional[str] = None) -> None:
    """
    Set default LLM client to use OpenAI.

    Args:
        model_name: which OpenAI's model should be used
        openai_api_key: OpenAI's API key - if None OPENAI_API_KEY environment variable will be used
    """
    global default_llm_client  # pylint: disable=W0603
    default_llm_client = OpenAIClient(model_name=model_name, api_key=openai_api_key)


def use_event_handler(event_handler: EventHandler) -> None:
    """
    Set default event handler to be used by all collections.

    Args:
        event_handler: The event handler to be used.
    """
    global default_event_handlers  # pylint: disable=W0602
    default_event_handlers.append(event_handler)


def create_collection(name: str, event_handlers: Optional[List[EventHandler]] = None) -> Collection:
    """
    Create a new collection that is a container for registering views, configuration and main entrypoint to db-ally
    features.

    Args:
         name: The name of the collection
         event_handlers: The event handlers to be used by the collection

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
    nl_responder = NLResponder(llm_client=llm_client)
    event_handlers = event_handlers or default_event_handlers

    return Collection(
        name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        iql_generator=iql_generator,
        event_handlers=event_handlers,
    )
