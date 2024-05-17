
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

Enabling LangSmith integration can be done by passing a prepared [EventHandler](../reference/event_handlers/index.md) when creating a db-ally collection:

```python
import dbally
from dbally.audit.event_handlers.langsmith_event_handler import LangSmithEventHandler

my_collection = dbally.create_collection(
    "collection_name",
    llm=LiteLLM(),
    event_handlers=[LangSmithEventHandler(api_key="your_api_key")],
)
```

After this, all the queries against the collection will be logged to LangSmith.
