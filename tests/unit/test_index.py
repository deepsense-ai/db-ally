import pytest

from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.index import GlobalEventHandlerClass, global_event_handlers


def test_singleton():
    handler1 = GlobalEventHandlerClass()
    handler2 = GlobalEventHandlerClass()
    assert handler1 is handler2


def test_add_item():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    assert len(global_event_handlers) == 1
    assert global_event_handlers[0] is handler


def test_add_item_invalid_type():
    global_event_handlers.clear_list()
    with pytest.raises(ValueError):
        global_event_handlers.add_item("not an event handler")


def test_remove_item():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    global_event_handlers.remove_item(handler)
    assert len(global_event_handlers) == 0


def test_get_list():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    assert global_event_handlers.get_list() == [handler]


def test_clear_list():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    global_event_handlers.clear_list()
    assert len(global_event_handlers) == 0


def test_getitem():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    assert global_event_handlers[0] is handler


def test_setitem():
    global_event_handlers.clear_list()
    handler1 = CLIEventHandler()
    handler2 = CLIEventHandler()
    global_event_handlers.add_item(handler1)
    global_event_handlers[0] = handler2
    assert global_event_handlers[0] is handler2


def test_setitem_invalid_type():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    with pytest.raises(ValueError):
        global_event_handlers[0] = "not an event handler"


def test_delitem():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    del global_event_handlers[0]
    assert len(global_event_handlers) == 0


def test_len():
    global_event_handlers.clear_list()
    assert len(global_event_handlers) == 0
    handler = CLIEventHandler()
    global_event_handlers.add_item(handler)
    assert len(global_event_handlers) == 1


def test_append():
    global_event_handlers.clear_list()
    handler = CLIEventHandler()
    global_event_handlers.append(handler)
    assert len(global_event_handlers) == 1
    assert global_event_handlers[0] is handler


def test_find_buffer():
    global_event_handlers.clear_list()
    handler = BufferEventHandler()
    global_event_handlers.add_item(handler)
    non_buffer_handler = CLIEventHandler()
    global_event_handlers.add_item(non_buffer_handler)
    global_event_handlers.remove_item(handler)
    assert global_event_handlers.find_buffer() is None
