# EventHandler Base Class

db-ally provides an `EventHandler` abstract class that can be used to log the runs of db-ally to any external systems.

!!! tip
    To learn how to create a cutom `EventHandler`, visit [How-To: Create your own event handler](../../how-to/create_custom_event_handler.md).

## Lifecycle

Each run of [dbally.Collection.ask][dbally.Collection.ask] will trigger all instances of EventHandler that were passed to the Collection's constructor (or the [dbally.create_collection][dbally.create_collection] function).


1. `EventHandler.request_start` is called with [RequestStart][dbally.audit.events.RequestStart], it can return a context object that will be passed to next calls.
2. For each event that occurs during the run, `EventHandler.event_start` is called with the context object returned by `EventHandler.request_start` and an Event object. It can return context for the `EventHandler.event_end` method.
3. When the event ends `EventHandler.event_end` is called with the context object returned by `EventHandler.event_start` and an Event object.
4. On the end of the run `EventHandler.request_end` is called with the context object returned by `EventHandler.request_start` and the [RequestEnd][dbally.audit.events.RequestEnd].


``` mermaid
sequenceDiagram
  participant C as Collection.ask()
  participant E as EventHandler
  C->>E: request_start(RequestStart(question, self.name))
  activate E
  E->>C: optional RequestCtx
  deactivate E
  loop every event
        C->>E: event_start(LLMEvent, RequestCtx)
        activate E
        E->>C: optional EventCtx
        deactivate E
        activate C
        C->>E: event_end(LLMEvent, RequestCtx, EventCtx)
        deactivate C
  end
  C->>E: request_end(RequestEnd, RequestCtx)
```

Currently handled events:

* Every call to the **LLM**

::: dbally.audit.EventHandler

::: dbally.audit.events.RequestStart

::: dbally.audit.events.RequestEnd

::: dbally.audit.events.Event

::: dbally.audit.events.LLMEvent

::: dbally.audit.events.SimilarityEvent

::: dbally.audit.spans.EventSpan
