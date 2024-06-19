from typing import List, Optional

from dbally.collection.multi_collection import MultiCollection

from .audit.event_handlers.base import EventHandler
from .collection import Collection
from .collection.single_collection import SingleCollection
from .llms import LLM
from .nl_responder.nl_responder import NLResponder
from .view_selection.base import ViewSelector
from .view_selection.llm_view_selector import LLMViewSelector


def create_collection(*args, **kwargs):
    """
    Create either a single collection or a multicollection based on the provided arguments.

    This function acts as a dispatcher to either `create_single_collection` or `create_multicollection`
    based on the value of the `is_single` parameter. It simplifies the creation process by abstracting
    the details of each type of collection.

    Args:
        *args: Positional arguments to be passed to the respective collection creation function.
        is_single (bool): If True, a single collection will be created. If False, a multicollection will be created.
        **kwargs: Keyword arguments to be passed to the respective collection creation function.

    Returns:
        Union[SingleCollection, MultiCollection]: An instance of either `SingleCollection` or `MultiCollection`
        based on the value of `is_single`.

    Raises:
        ValueError: if required arguments for the selected collection type are missing or invalid.

    Examples:
        Creating a single collection:
        ```python
        from dbally import create_collection
        from dbally.llms.litellm import LiteLLM

        collection = create_collection(is_single=True, "my_collection", llm=LiteLLM())
        ```

        Creating a multicollection:
        ```python
        from dbally import create_collection, Collection

        collection1 = Collection("collection1")
        collection2 = Collection("collection2")
        multicollection = create_collection(is_single=False, "my_multicollection", [collection1, collection2])
        ```
    """
    is_multi = kwargs.get("is_multi")
    if is_multi:
        return create_multi_collection(args, kwargs)

    return create_single_collection(args, kwargs)


def create_single_collection(
    name: str,
    llm: LLM,
    event_handlers: Optional[List[EventHandler]] = None,
    view_selector: Optional[ViewSelector] = None,
    nl_responder: Optional[NLResponder] = None,
) -> SingleCollection:
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
    event_handlers = event_handlers or []

    return SingleCollection(
        name=name,
        nl_responder=nl_responder,
        view_selector=view_selector,
        llm=llm,
        event_handlers=event_handlers,
    )


def create_multi_collection(name: str, collection_list: List[SingleCollection]) -> MultiCollection:
    """
    Create a new [Multicollection](multicollection.md) that is a container for registering list of views and the\
    main entrypoint to db-ally features.

    Args:
        name: Name of the Multicollection
        collection_list: List of registered collections.

    Returns:
        a new instance of db-ally Multicollection

    """
    return MultiCollection(name, collection_list)
