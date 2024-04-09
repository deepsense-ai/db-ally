# EventHandler Base Class

db-ally provides an `EventHandler` abstract class that can be used to log the runs of db-ally to any external systems.

!!! tip
    To learn how to create a cutom `EventHandler`, visit [How-To: Create your own event handler](../../how-to/create_custom_event_handler.md).




## Lifecycle


Every run of [dbally.Collection.ask](../collection.md/#collection.ask) will trigger every instance of EventHandler that was registered using [`dbally.use_event_handler`](../index.md/#dbally.use_event_handler) method in following manner:


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

::: dbally.audit.event_handlers.EventHandler

::: dbally.data_models.audit.RequestStart

::: dbally.data_models.audit.RequestEnd

::: dbally.data_models.audit.LLMEvent
