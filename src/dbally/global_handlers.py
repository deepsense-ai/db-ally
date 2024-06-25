from typing import List, Optional, Type

from dbally.audit.event_handlers import EventHandler
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler

# Global list of event handlers initialized with a default CLIEventHandler.
global_event_handlers_list: List[EventHandler] = [CLIEventHandler()]


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
    global global_event_handlers_list  # pylint: disable=global-statement
    global_event_handlers_list = event_handler_list


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
    global_event_handlers_list.append(event_handler)


def find_event_handler(object_type: Type) -> Optional[EventHandler]:
    """
    Finds an event handler of the specified type from a list of event handlers.

    Args:
        object_type: The type of the event handler to find.

    Returns:
        The first event handler of the specified type if found, otherwise None.
    """
    for single_event_handler in global_event_handlers_list:
        if type(single_event_handler) is object_type:  # pylint: disable=unidiomatic-typecheck
            return single_event_handler
    return None
