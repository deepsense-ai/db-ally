# EventHandler

db-ally provides an `EventHandler` abstract class that can be used to log the runs of db-ally to any external systems.


## Lifecycle


Every run of db-ally will initialize any instance of EventHandler that was registered using `dbally.use_event_handler` method.

1. `EventHandler.request_start` is called with [RequestStart](#dbally.data_models.audit.RequestStart), it can return a context object that will be passed to next calls.
2. For each event that occurs during the run, `EventHandler.event_start` is called with an Event and the context object returned by `EventHandler.request_start`. It can return context for the event_end method.
3. When the event ends `EventHandler.event_end` is called with an Event and the context object returned by `EventHandler.event_start`.
4. On the end of the run `EventHandler.request_end` is called with [RequestEnd](#dbally.data_models.audit.RequestEnd) and the context object returned by `EventHandler.request_start`.

::: dbally.audit.event_handlers.EventHandler

::: dbally.data_models.audit.RequestStart

::: dbally.data_models.audit.RequestEnd
