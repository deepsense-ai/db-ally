from typing import List, Optional, Type

from .audit import CLIEventHandler
from .audit.event_handlers.base import EventHandler
from .collection import Collection
from .llms import LLM
from .nl_responder.nl_responder import NLResponder
from .view_selection.base import ViewSelector
from .view_selection.llm_view_selector import LLMViewSelector

# Global list of event handlers initialized with a default CLIEventHandler.
event_handlers: List[EventHandler] = [CLIEventHandler()]


def set_event_handlers(event_handler_list: List[EventHandler]) -> None:
    """
    Set the global list of event handlers.

    This function replaces the current list of event handlers with the provided list.
    It ensures that each handler in the provided list is an instance of EventHandler.
    If any handler is not an instance of EventHandler, it raises a ValueError.

    Args:
        event_handler_list (List[EventHandler]): The list of event handlers to set.

    Raises:
        ValueError: If any handler in the list is not an instance of EventHandler.
    """
    for handler in event_handler_list:
        if isinstance(type(handler), EventHandler):
            raise ValueError(f"{handler} is not an instance of EventHandler")
    global event_handlers  # pylint: disable=global-statement
    event_handlers = event_handler_list


def add_event_handler(event_handler: EventHandler) -> None:
    """
    Add an event handler to the global list.

    This function appends the provided event handler to the global list of event handlers.
    It ensures that the handler is an instance of EventHandler.
    If the handler is not an instance of EventHandler, it raises a ValueError.

    Args:
        event_handler (EventHandler): The event handler to add.

    Raises:
        ValueError: If the handler is not an instance of EventHandler.
    """
    if isinstance(type(event_handler), EventHandler):
        raise ValueError(f"{event_handler} is not an instance of EventHandler")
    event_handlers.append(event_handler)


def find_event_handler(object_type: Type):
    """
    Finds an event handler of the specified type from a list of event handlers.

    Args:
        object_type (Type[Any]): The type of the event handler to find.

    Returns:
        Optional[Any]: The first event handler of the specified type if found,
                       otherwise None.
    """
    for event_handler in event_handlers:
        if type(event_handler) is object_type:  # pylint disable=unidiomatic-typecheck
            return event_handler
    return None


def create_collection(
    name: str,
    llm: LLM,
    collection_event_handlers: Optional[List[EventHandler]] = None,
    view_selector: Optional[ViewSelector] = None,
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
        from dbally.llms.litellm import LiteLLM

        collection = create_collection("my_collection", llm=LiteLLM())
    ```

    Args:
        name: Name of the collection is available for [Event handlers](event_handlers/index.md) and is\
        used to distinguish different db-ally runs.
        llm: LLM used by the collection to generate responses for natural language queries.
        collection_event_handlers: Event handlers used by the collection during query executions. Can be used to\
        log events as [CLIEventHandler](event_handlers/cli_handler.md) or to validate system performance as\
        [LangSmithEventHandler](event_handlers/langsmith_handler.md).
        view_selector: View selector used by the collection to select the best view for the given query.\
        If None, a new instance of [LLMViewSelector][dbally.view_selection.llm_view_selector.LLMViewSelector]\
        will be used.
        nl_responder: NL responder used by the collection to respond to natural language queries. If None,\
        a new instance of [NLResponder][dbally.nl_responder.nl_responder.NLResponder] will be used.

    Returns:
        a new instance of db-ally Collection

    Raises:
        ValueError: if default LLM client is not configured
    """
    view_selector = view_selector or LLMViewSelector(llm=llm)
    nl_responder = nl_responder or NLResponder(llm=llm)

    collection_event_handlers = collection_event_handlers or event_handlers

    return Collection(
        name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        llm=llm,
        collection_event_handlers=collection_event_handlers,
    )
