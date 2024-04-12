# EventHandler Base Class

db-ally provides an `EventHandler` abstract class that can be used to log the runs of db-ally to any external systems.

!!! tip
    To learn how to create a cutom `EventHandler`, visit [How-To: Create your own event handler](../../how-to/create_custom_event_handler.md).

## Lifecycle

Each run of [dbally.Collection.ask][dbally.Collection.ask] will trigger all instances of EventHandler registered using [`dbally.use_event_handler`][dbally.use_event_handler].


1. `EventHandler.request_start` is called with [RequestStart][dbally.data_models.audit.RequestStart], it can return a context object that will be passed to next calls.
2. For each event that occurs during the run, `EventHandler.event_start` is called with the context object returned by `EventHandler.request_start` and an Event object. It can return context for the `EventHandler.event_end` method.
3. When the event ends `EventHandler.event_end` is called with the context object returned by `EventHandler.event_start` and an Event object.
4. On the end of the run `EventHandler.request_end` is called with the context object returned by `EventHandler.request_start` and the [RequestEnd][dbally.data_models.audit.RequestEnd].


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

::: dbally.data_models.audit.RequestStart

::: dbally.data_models.audit.RequestEnd

::: dbally.data_models.audit.LLMEvent
