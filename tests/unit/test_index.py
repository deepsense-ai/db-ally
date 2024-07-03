import pytest

from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.index import GlobalEventHandlerClass, event_handlers


def test_singleton():
    handler1 = GlobalEventHandlerClass()
    handler2 = GlobalEventHandlerClass()
    assert handler1 is handler2


def test_add_item():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    assert len(event_handlers) == 1
    assert event_handlers[0] is handler


def test_add_item_invalid_type():
    event_handlers.clear_list()
    with pytest.raises(ValueError):
        event_handlers.add_item("not an event handler")


def test_remove_item():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    event_handlers.remove_item(handler)
    assert len(event_handlers) == 0


def test_get_list():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    assert event_handlers.get_list() == [handler]


def test_clear_list():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    event_handlers.clear_list()
    assert len(event_handlers) == 0


def test_getitem():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    assert event_handlers[0] is handler


def test_setitem():
    event_handlers.clear_list()
    handler1 = CLIEventHandler()
    handler2 = CLIEventHandler()
    event_handlers.add_item(handler1)
    event_handlers[0] = handler2
    assert event_handlers[0] is handler2


def test_setitem_invalid_type():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    with pytest.raises(ValueError):
        event_handlers[0] = "not an event handler"


def test_delitem():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    del event_handlers[0]
    assert len(event_handlers) == 0


def test_len():
    event_handlers.clear_list()
    assert len(event_handlers) == 0
    handler = CLIEventHandler()
    event_handlers.add_item(handler)
    assert len(event_handlers) == 1


def test_append():
    event_handlers.clear_list()
    handler = CLIEventHandler()
    event_handlers.append(handler)
    assert len(event_handlers) == 1
    assert event_handlers[0] is handler


def test_find_buffer():
    event_handlers.clear_list()
    handler = BufferEventHandler()
    event_handlers.add_item(handler)
    non_buffer_handler = CLIEventHandler()
    event_handlers.add_item(non_buffer_handler)
    event_handlers.remove_item(handler)
    assert event_handlers.find_buffer() is None
