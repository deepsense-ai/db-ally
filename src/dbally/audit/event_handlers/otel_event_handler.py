import json
from typing import Optional

from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, StatusCode, TracerProvider

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.events import Event, LLMEvent, RequestEnd, RequestStart, SimilarityEvent

TRACER_NAME = "db-ally.events"


class OtelEventHandler(EventHandler[Span, Span]):
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

    async def request_start(self, user_request: RequestStart) -> Span:
        """
        Initializes new OTel Span as a parent.

        Args:
            user_request: The start of the request.

        Returns:
            span object as a parent for all subsequent events for this request
        """
        with self.tracer.start_as_current_span("request", end_on_exit=False, kind=SpanKind.SERVER) as span:
            span.set_attribute("db-ally.user.collection", user_request.collection_name)
            if self.record_inputs:
                span.set_attribute("db-ally.user.question", user_request.question)

            return span

    async def event_start(self, event: Event, request_context: Span) -> Span:
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
                span.set_attribute("db-ally.llm.type", event.type)
                if self.record_inputs:
                    span.set_attribute("db-ally.llm.prompts", json.dumps(event.prompt))

            return span

        if isinstance(event, SimilarityEvent):
            with self._new_child_span(request_context, "similarity") as span:
                span.set_attributes(
                    {
                        "db-ally.similarity.store": event.store,
                        "db-ally.similarity.fetcher": event.fetcher,
                    }
                )
                if self.record_inputs:
                    span.set_attribute("db-ally.similarity.input", event.input_value)

            return span

        raise ValueError(f"Unsuported event: {type(event)}")

    async def event_end(self, event: Optional[Event], request_context: Span, event_context: Span) -> None:
        """
        Finalizes execution of the event, ending a span for this event.

        Args:
            event: optional event information
            request_context: parent span
            event_context: event span
        """

        if isinstance(event, LLMEvent):
            event_context.set_attribute("db-ally.llm.response-tokes", event.completion_tokens)
            if self.record_outputs:
                event_context.set_attribute("db-ally.llm.response", event.response)

        if isinstance(event, SimilarityEvent) and self.record_outputs:
            event_context.set_attribute("db-ally.similarity.output", event.output_value)

        event_context.set_status(StatusCode.OK)
        event_context.end()

    async def request_end(self, output: RequestEnd, request_context: Span) -> None:
        """
        Finalizes entire request, ending the span for this request.

        Args:
            output: output generated for this request
            request_context: span to be closed
        """
        if self.record_outputs:
            request_context.set_attribute("db-ally.response", output.result.textual_response)

        request_context.set_status(StatusCode.OK)
        request_context.end()

    def _new_child_span(self, parent: Span, name: str):
        context = trace.set_span_in_context(parent)
        return self.tracer.start_as_current_span(name, context=context, end_on_exit=False, kind=SpanKind.CLIENT)
