from typing import List, Optional

from .audit.event_handlers.base import EventHandler
from .collection import Collection
from .iql_generator.iql_generator import IQLGenerator
from .llm_client.base import LLMClient
from .nl_responder.nl_responder import NLResponder
from .view_selection.base import ViewSelector
from .view_selection.llm_view_selector import LLMViewSelector


def create_collection(
    name: str,
    llm_client: LLMClient,
    event_handlers: Optional[List[EventHandler]] = None,
    view_selector: Optional[ViewSelector] = None,
    iql_generator: Optional[IQLGenerator] = None,
    nl_responder: Optional[NLResponder] = None,
) -> Collection:
    """
    Create a new [Collection](collection.md) that is a container for registering views and the\
    main entrypoint to db-ally features.

    Unlike instantiating a [Collection][dbally.Collection] directly, this function\
    provides a set of default values for various dependencies like LLM client, view selector,\
    IQL generator, and NL responder.

    ##Example

    ```python
        from dbally import create_collection
        from dbally.llm_client.openai_client import OpenAIClient

        collection = create_collection("my_collection", llm_client=OpenAIClient())
    ```

    Args:
        name: Name of the collection is available for [Event handlers](event_handlers/index.md) and is\
        used to distinguish different db-ally runs.
        llm_client: LLM client used by the collection to generate views and respond to natural language\
        queries.
        event_handlers: Event handlers used by the collection during query executions. Can be used to\
        log events as [CLIEventHandler](event_handlers/cli_handler.md) or to validate system performance as\
        [LangSmithEventHandler](event_handlers/langsmith_handler.md).
        view_selector: View selector used by the collection to select the best view for the given query.\
        If None, a new instance of [LLMViewSelector][dbally.view_selection.llm_view_selector.LLMViewSelector]\
        will be used.
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
    view_selector = view_selector or LLMViewSelector(llm_client=llm_client)
    iql_generator = iql_generator or IQLGenerator(llm_client=llm_client)
    nl_responder = nl_responder or NLResponder(llm_client=llm_client)
    event_handlers = event_handlers or []

    return Collection(
        name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        iql_generator=iql_generator,
        event_handlers=event_handlers,
    )
