import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, StatusCode, TracerProvider
from opentelemetry.util.types import AttributeValue

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.events import Event, FallbackEvent, LLMEvent, RequestEnd, RequestStart, SimilarityEvent

TRACER_NAME = "db-ally.events"
FORBIDDEN_CONTEXT_KEYS = {"filter_mask"}

TransformFn = Optional[Callable[[Any], Optional[AttributeValue]]]


def _optional_str(value: Optional[any]) -> Optional[str]:
    return None if value is None else str(value)


@dataclass
class SpanHandler:
    """Handles span attributes and lifecycle"""

    span: Span
    record_inputs: bool
    record_outputs: bool

    def set(self, key: str, value: Optional[Any], transform: TransformFn = None) -> "SpanHandler":
        """
        Sets a value as span attribute under given key if the value exists. Optionally one can add transform function to
        change value from any to valid OpenTelemetry attribute type.

        Args:
            key: attribute name
            value: attribute value. If None, the value is not set
            transform: optional function to transform from Any to valid OTel AttributeValue

        Returns:
            self, for chaining calls
        """
        value = value if transform is None else transform(value)
        if value is not None:
            self.span.set_attribute(key, value)

        return self

    def set_input(self, key: str, value: Optional[Any], transform: TransformFn = None) -> "SpanHandler":
        """
        Sets a value, that is used as model input, under given key if the value exists. If the class does not record
        inputs, then the value is not set. Optionally one can add transform function to change value from any to valid
        OpenTelemetry attribute type.

        Args:
            key: attribute name
            value: attribute value. If None, the value is not set. If record_inputs is False, the value is not set.
            transform: optional function to transform from Any to valid OTel AttributeValue

        Returns:
            self, for chaining calls
        """
        value = value if transform is None else transform(value)
        if value is not None and self.record_inputs:
            self.span.set_attribute(key, value)

        return self

    def set_output(self, key: str, value: Optional[Any], transform: TransformFn = None) -> "SpanHandler":
        """
        Sets a value, that is the model output under, given key if the value exists. If the class does not record
        inputs, then the value is not set. Optionally one can add transform function to change value from any to valid
        OpenTelemetry attribute type.

        Args:
            key: attribute name
            value: attribute value. If None, the value is not set. If record_output is False, the value is not set.
            transform: optional function to transform from Any to valid OTel AttributeValue

        Returns:
            self, for chaining calls
        """
        value = value if transform is None else transform(value)
        if value is not None and self.record_outputs:
            self.span.set_attribute(key, value)

        return self

    def end_succesfully(self) -> None:
        """Sets status of the span to OK and ends the span with current time"""
        self.span.set_status(StatusCode.OK)
        self.span.end()


class OtelEventHandler(EventHandler[SpanHandler, SpanHandler]):
    """
    This handler emits OpenTelemetry spans for recorded events.
    """

    def __init__(
        self, provider: Optional[TracerProvider] = None, record_inputs: bool = True, record_outputs: bool = True
    ) -> None:
        """
        Initialize OtelEventHandler. By default, it will try to use globaly configured TracerProvider. Pass it
        explicitly if you want custom implementation, or you do not use OTel auto-instrumentation.

        To comply with the
        [OTel Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/llm-spans/#configuration)
        recording of inputs and outputs can be disabled.

        Args:
            provider: Optional tracer provider. By default global provider is used.
            record_inputs: if true (default) all inputs are recorded as span attributes. Depending on usecase it maybe
                           turned off, to save resources and improve performance.
            record_outputs: if true (default) all outputs are recorded as span attributes. Depending on usecase it
                            maybe turned off, to save resources and improve performance.
        """
        self.record_inputs = record_inputs
        self.record_outputs = record_outputs
        if provider is None:
            self.tracer = trace.get_tracer(TRACER_NAME)
        else:
            self.tracer = provider.get_tracer(TRACER_NAME)

    def _handle_span(self, span: Span) -> SpanHandler:
        return SpanHandler(span, self.record_inputs, self.record_outputs)

    async def request_start(self, user_request: RequestStart) -> SpanHandler:
        """
        Initializes new OTel Span as a parent.

        Args:
            user_request: The start of the request.

        Returns:
            span object as a parent for all subsequent events for this request
        """
        with self.tracer.start_as_current_span("request", end_on_exit=False, kind=SpanKind.SERVER) as span:
            return (
                self._handle_span(span)
                .set("db-ally.user.collection", user_request.collection_name)
                .set_input("db-ally.user.question", user_request.question)
            )

    async def event_start(self, event: Event, request_context: SpanHandler) -> SpanHandler:
        """
        Starts a new event in a system as a span. Uses request span as a parent.

        Args:
            event: Event to register
            request_context: Parent span for this event

        Returns:
            span object capturing start of execution for this event

        Raises:
            ValueError: it is thrown when unknown event type is passed as argument
        """
        if isinstance(event, LLMEvent):
            with self._new_child_span(request_context, "llm") as span:
                return (
                    self._handle_span(span)
                    .set("db-ally.llm.type", event.type)
                    .set_input("db-ally.llm.prompts", json.dumps(event.prompt))
                )

        if isinstance(event, SimilarityEvent):
            with self._new_child_span(request_context, "similarity") as span:
                return (
                    self._handle_span(span)
                    .set("db-ally.similarity.store", event.store)
                    .set("db-ally.similarity.fetcher", event.fetcher)
                    .set_input("db-ally.similarity.input", event.input_value)
                )
        if isinstance(event, FallbackEvent):
            with self._new_child_span(request_context, "fallback") as span:
                return self._handle_span(span).set("db-ally.error_description", event.error_description)

        raise ValueError(f"Unsupported event: {type(event)}")

    async def event_end(self, event: Optional[Event], request_context: SpanHandler, event_context: SpanHandler) -> None:
        """
        Finalizes execution of the event, ending a span for this event.

        Args:
            event: optional event information
            request_context: parent span
            event_context: event span
        """

        if isinstance(event, LLMEvent):
            event_context.set("db-ally.llm.response-tokes", event.completion_tokens).set_output(
                "db-ally.llm.response", event.response
            )

        if isinstance(event, SimilarityEvent) and self.record_outputs:
            event_context.set("db-ally.similarity.output", event.output_value)

        event_context.end_succesfully()

    async def request_end(self, output: RequestEnd, request_context: SpanHandler) -> None:
        """
        Finalizes entire request, ending the span for this request.

        Args:
            output: output generated for this request
            request_context: span to be closed
        """
        request_context.set_output("db-ally.result.textual", output.result.textual_response).set(
            "db-ally.result.execution-time", output.result.execution_time
        ).set("db-ally.result.execution-time-view", output.result.execution_time_view).set(
            "db-ally.result.view-name", output.result.view_name
        )

        for key, value in output.result.context.items():
            if key not in FORBIDDEN_CONTEXT_KEYS:
                request_context.set(f"db-ally.result.context.{key}", value, transform=_optional_str)

        request_context.end_succesfully()

    def _new_child_span(self, parent: SpanHandler, name: str):
        context = trace.set_span_in_context(parent.span)
        return self.tracer.start_as_current_span(name, context=context, end_on_exit=False, kind=SpanKind.CLIENT)
