from typing import List, Optional

from .audit.event_handlers.base import EventHandler
from .collection import Collection
from .iql_generator.iql_generator import IQLGenerator
from .llm_client.base import LLMClient
from .llm_client.openai_client import OpenAIClient
from .nl_responder.nl_responder import NLResponder
from .view_selection.base import ViewSelector
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
    llm_client: Optional[LLMClient] = None,
    view_selector: Optional[ViewSelector] = None,
    iql_generator: Optional[IQLGenerator] = None,
    nl_responder: Optional[NLResponder] = None,
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
        llm_client: LLM client used by the collection to generate views and respond to natural language\
        queries. If None, the default LLM client will be used.
        view_selector: View selector used by the collection to select the best view for the given query.\
        If None, a new instance of [LLMViewSelector][dbally.view_selection.LLMViewSelector] will be used.
        iql_generator: IQL generator used by the collection to generate IQL queries from natural language\
        queries. If None, a new instance of [IQLGenerator][dbally.iql_generator.iql_generator.IQLGenerator]\
        will be used.
        nl_responder: NL responder used by the collection to respond to natural language queries. If None,\
        a new instance of [NLResponder][dbally.nl_responder.nl_responder.NLResponder] will be used.

    Returns:
        a new instance of db-ally Collection

    Raises:
        ValueError: if default LLM client is not configured
    """
    llm_client = llm_client or default_llm_client

    if not llm_client:
        raise ValueError("LLM client is not configured. Pass the llm_client argument or set the default llm client")

    view_selector = view_selector or LLMViewSelector(llm_client=llm_client)
    iql_generator = iql_generator or IQLGenerator(llm_client=llm_client)
    nl_responder = nl_responder or NLResponder(llm_client=llm_client)
    event_handlers = event_handlers or default_event_handlers

    return Collection(
        name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        iql_generator=iql_generator,
        event_handlers=event_handlers,
    )
