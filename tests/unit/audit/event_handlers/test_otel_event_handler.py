from typing import Dict, Mapping, Sequence

from opentelemetry import trace
from opentelemetry.trace import Span, StatusCode

from dbally.audit.event_handlers.otel_event_handler import SpanHandler


class MockSpan(Span):
    def __init__(self) -> None:
        super().__init__()
        self.attributes = {}
        self.status = StatusCode.UNSET
        self.is_finished = False

    def end(self, end_time: int | None = None) -> None:
        self.is_finished = True

    def get_span_context(self) -> trace.SpanContext:
        raise NotImplementedError

    def set_attributes(
        self,
        attributes: Dict[
            str, str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float]
        ],
    ) -> None:
        self.attributes |= attributes

    def set_attribute(
        self,
        key: str,
        value: str
        | bool
        | int
        | float
        | trace.Sequence[str]
        | trace.Sequence[bool]
        | trace.Sequence[int]
        | trace.Sequence[float],
    ) -> None:
        self.attributes[key] = value

    def add_event(
        self,
        name: str,
        attributes: Mapping[
            str, str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float]
        ]
        | None = None,
        timestamp: int | None = None,
    ) -> None:
        raise NotImplementedError

    def update_name(self, name: str) -> None:
        raise NotImplementedError

    def is_recording(self) -> bool:
        raise NotImplementedError

    def set_status(self, status: trace.Status | StatusCode, description: str | None = None) -> None:
        self.status = status.status_code if isinstance(status, trace.Status) else status

    def record_exception(
        self,
        exception: BaseException,
        attributes: Mapping[
            str, str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float]
        ]
        | None = None,
        timestamp: int | None = None,
        escaped: bool = False,
    ) -> None:
        raise NotImplementedError


def test_span_handler_sets_all():
    span = MockSpan()

    handler = SpanHandler(span, record_inputs=True, record_outputs=True)
    handler.set("standard", "1")
    handler.set_input("inputs", "2")
    handler.set_output("outputs", "3")
    handler.end_succesfully()

    assert span.attributes.get("standard") == "1"
    assert span.attributes.get("inputs") == "2"
    assert span.attributes.get("outputs") == "3"
    assert span.status == StatusCode.OK
    assert span.is_finished


def test_span_handler_sets_without_input():
    span = MockSpan()

    handler = SpanHandler(span, record_inputs=False, record_outputs=True)
    handler.set("standard", "1")
    handler.set_input("inputs", "2")
    handler.set_output("outputs", "3")
    handler.end_succesfully()

    assert span.attributes.get("standard") == "1"
    assert span.attributes.get("inputs") is None
    assert span.attributes.get("outputs") == "3"
    assert span.status == StatusCode.OK
    assert span.is_finished


def test_span_handler_sets_without_outputs():
    span = MockSpan()

    handler = SpanHandler(span, record_inputs=True, record_outputs=False)
    handler.set("standard", "1")
    handler.set_input("inputs", "2")
    handler.set_output("outputs", "3")
    handler.end_succesfully()

    assert span.attributes.get("standard") == "1"
    assert span.attributes.get("inputs") == "2"
    assert span.attributes.get("outputs") is None
    assert span.status == StatusCode.OK
    assert span.is_finished


def test_span_handler_sets_with_transformation():
    span = MockSpan()

    def transform_fn(x: str):
        return None if x == "foo" else x.upper()

    handler = SpanHandler(span, record_inputs=True, record_outputs=True)
    handler.set("standard", "foo", transform=transform_fn)
    handler.set_input("inputs", "bar", transform=transform_fn)
    handler.set_output("outputs", "baz", transform=transform_fn)
    handler.end_succesfully()

    assert span.attributes.get("standard") is None
    assert span.attributes.get("inputs") == "BAR"
    assert span.attributes.get("outputs") == "BAZ"
    assert span.status == StatusCode.OK
    assert span.is_finished
