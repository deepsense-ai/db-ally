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


def use_openai_llm(
    model_name: str = "gpt-3.5-turbo",
    openai_api_key: Optional[str] = None,
) -> None:
    """
    Set the default LLM client to the [OpenAIClient](llm/openai.md).

    Args:
        model_name: Name of the [OpenAI's model](https://platform.openai.com/docs/models) to be used.
        openai_api_key: OpenAI's API key. If None OPENAI_API_KEY environment variable will be used"
    """
    global default_llm_client  # pylint: disable=W0603
    default_llm_client = OpenAIClient(model_name=model_name, api_key=openai_api_key)


def use_event_handler(event_handler: EventHandler) -> None:
    """
    Add the given [event handler](event_handlers/index.md) to the list of default event handlers that \
    are used by all collections.

    Args:
        event_handler: [event handler](event_handlers/index.md)
    """
    global default_event_handlers  # pylint: disable=W0602
    default_event_handlers.append(event_handler)


def create_collection(
    name: str,
    event_handlers: Optional[List[EventHandler]] = None,
) -> Collection:
    """
    Create a new [Collection](collection.md) that is a container for registering views and the\
    main entrypoint to db-ally features.

    ##Example

    ```python
        from dbally import create_collection
        from dbally.audit.event_handlers.cli import CLIEventHandler

        collection = create_collection("my_collection", event_handlers=[CLIEventHandler()])
    ```

    Args:
        name: Name of the collection is available for [Event handlers](event_handlers/index.md) and is\
        used to distinguish different db-ally runs.
        event_handlers: Event handlers used by the collection during query executions. Can be used to\
        log events as [CLIEventHandler](event_handlers/cli.md) or to validate system performance as\
        [LangSmithEventHandler](event_handlers/langsmith.md).

    Returns:
        a new instance of db-ally Collection

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
