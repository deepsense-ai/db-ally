
# How-To: Log db-ally runs to LangSmith

[LangSmith](https://www.langchain.com/langsmith) can be utilized to log the runs of db-ally.

It serves as a useful tool to keep an overall track of the queries executed and to monitor the performance of the system.

This guide aims to demonstrate the process of logging the executions of db-ally to LangSmith.


## Prerequisites

1. Optional dependencies need to be installed to use LangSmith integration. Execute the command below to install these:

    ```bash
    pip install dbally[langsmith]
    ```

2. You need to have a LangSmith API key. Sign up at [LangSmith](https://smith.langchain.com/) to get one.


## Logging runs to LangSmith

Enabling LangSmith integration can be done by registering a prepared [EventHandler](../reference/event_handlers/index.md) using the `dbally.use_event_handler` method.

```python
import dbally
from dbally.audit.event_handlers.langsmith_event_handler import LangSmithEventHandler

dbally.use_event_handler(LangSmithEventHandler(api_key="your_api_key"))
```

After this, all the runs of db-ally will be logged to LangSmith.
