from typing import TYPE_CHECKING, List, Optional

from dbally.audit import EventHandler
from dbally.llms import LLM
from dbally.nl_responder.nl_responder import NLResponder
from dbally.view_selection import LLMViewSelector
from dbally.view_selection.base import ViewSelector

if TYPE_CHECKING:
    from dbally.collection import Collection


def create_collection(
    name: str,
    llm: LLM,
    event_handlers: Optional[List[EventHandler]] = None,
    view_selector: Optional[ViewSelector] = None,
    nl_responder: Optional[NLResponder] = None,
) -> "Collection":
    """
    Create a new [Collection](collection.md) that is a container for registering views and the\
    main entrypoint to db-ally features.

    Unlike instantiating a [Collection][dbally.Collection] directly, this function\
    provides a set of default values for various dependencies like LLM client, view selector,\
    IQL generator, and NL responder.

    ##Example

    ```python
        from dbally import create_collection
        from dbally.llms.litellm import LiteLLM

        collection = create_collection("my_collection", llm=LiteLLM())
    ```

    Args:
        name: Name of the collection is available for [Event handlers](event_handlers/index.md) and is\
        used to distinguish different db-ally runs.
        llm: LLM used by the collection to generate responses for natural language queries.
        event_handlers: Event handlers used by the collection during query executions. Can be used to\
        log events as [CLIEventHandler](event_handlers/cli_handler.md) or to validate system performance as\
        [LangSmithEventHandler](event_handlers/langsmith_handler.md). If provided, this parameter overrides the
        global dbally.event_handlers.
        view_selector: View selector used by the collection to select the best view for the given query.\
        If None, a new instance of [LLMViewSelector][dbally.view_selection.llm_view_selector.LLMViewSelector]\
        will be used.
        nl_responder: NL responder used by the collection to respond to natural language queries. If None,\
        a new instance of [NLResponder][dbally.nl_responder.nl_responder.NLResponder] will be used.

    Returns:
        New instance of db-ally Collection.

    Raises:
        ValueError: If default LLM client is not configured.
    """
    from dbally.collection import Collection  # pylint: disable=import-outside-toplevel

    view_selector = view_selector or LLMViewSelector(llm=llm)
    nl_responder = nl_responder or NLResponder(llm=llm)

    return Collection(
        name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        llm=llm,
        event_handlers=event_handlers,
    )
