from typing import Union, List

from .audit import EventHandler
from .audit.event_handlers.buffer_event_handler import BufferEventHandler


def singleton(self):
    """
    A decorator to make a class a singleton.

    Args:
        self: The class to be made singleton.

    Returns:
        function: A function that returns the single instance of the class.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Returns the single instance of the decorated class, creating it if necessary.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            object: The single instance of the class.
        """
        if self not in instances:
            instances[self] = self(*args, **kwargs)
        return instances[self]

    return get_instance


@singleton
class GlobalEventHandlerClass:
    """
    A singleton class to manage a list of event handlers.
    """

    def __init__(self):
        """
        A singleton class to manage a list of event handlers.
        """
        self._list = []

    def add_item(self, item: EventHandler):
        """
        Adds an event handler to the list.

        Args:
            item: The event handler to add.

        Raises:
            ValueError: If the item is not an instance of EventHandler.
        """
        if not isinstance(item, EventHandler):
            raise ValueError(f"Handler {item} is not EventHandler type")
        self._list.append(item)

    def remove_item(self, item: EventHandler):
        """
        Removes an event handler from the list.

        Args:
            item (EventHandler): The event handler to remove.
        """
        self._list.remove(item)

    def get_list(self):
        """
        Returns the list of event handlers.

        Returns:
            list: The list of event handlers.
        """
        return self._list

    def clear_list(self):
        """
        Clears the list of event handlers.
        """
        self._list.clear()

    def __getitem__(self, index: int):
        """
        Gets the event handler at the specified index.

        Args:
            index: The index of the event handler to get.

        Returns:
            EventHandler: The event handler at the specified index.
        """
        return self._list[index]

    def __setitem__(self, index: int, value: EventHandler):
        """
        Sets the event handler at the specified index.

        Args:
            index (int): The index at which to set the event handler.
            value (EventHandler): The event handler to set.

        Raises:
            ValueError: If the value is not an instance of EventHandler.
        """
        if not isinstance(value, EventHandler):
            raise ValueError(f"Handler {value} is not EventHandler type")
        self._list[index] = value

    def __delitem__(self, index: int):
        """
        Deletes the event handler at the specified index.

        Args:
            index (int): The index of the event handler to delete.
        """
        del self._list[index]

    def __len__(self):
        """
        Returns the number of event handlers in the list.

        Returns:
            int: The number of event handlers.
        """
        return len(self._list)

    def __eq__(self, other: Union[list, "GlobalEventHandlerClass"]):
        """
        Determine if this instance is equal to another object.

        The comparison is based on the equality of the `_list` attribute.
        If the other object is an instance of `GlobalEventHandlerClass`,
        their `_list` attributes are compared. If the other object is a list,
        it is compared directly to this instance's `_list` attribute.

        Args:
            other (object): The object to compare with this instance.

        Returns:
            bool: True if the objects are considered equal, False otherwise.

        Raises:
            NotImplemented: If the `other` object is neither a `GlobalEventHandlerClass`
                            instance nor a list.
        """
        if isinstance(other, type(self)):
            return self._list == other._list
        if isinstance(other, list):
            return self._list == other
        return NotImplemented

    def __ne__(self, other: Union[list, "GlobalEventHandlerClass"]):
        """
        Determine if this instance is not equal to another object.

        The comparison is based on the inequality of the `_list` attribute.
        If the other object is an instance of `GlobalEventHandlerClass`,
        their `_list` attributes are compared. If the other object is a list,
        it is compared directly to this instance's `_list` attribute.

        Args:
            other (object): The object to compare with this instance.

        Returns:
            bool: True if the objects are considered not equal, False otherwise.

        Raises:
            NotImplemented: If the `other` object is neither a `GlobalEventHandlerClass`
                            instance nor a list.
        """
        if isinstance(other, type(self)):
            return self._list != other._list
        if isinstance(other, list):
            return self._list != other
        return NotImplemented

    def set(self, value: List[EventHandler]):
        """

        Args:
            value:

        Returns:

        """
        self._list = value

    def append(self, value):
        """
        Appends an event handler to the list.

        Args:
            value (EventHandler): The event handler to append.
        """
        self.add_item(value)

    def find_buffer(self):
        """
        Finds and returns the buffer of a BufferEventHandler in the list.

        Returns:
            Buffer: The buffer of a BufferEventHandler if found, None otherwise.
        """
        for handler in self._list:
            if isinstance(handler, BufferEventHandler):  # pylint: disable=C0123
                return handler.buffer
        return None


# Global instance of the event handler singleton
event_handlers = GlobalEventHandlerClass()
