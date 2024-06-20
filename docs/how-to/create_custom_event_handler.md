# How-To: Create your own event handler

db-ally offers an expandable event handler system. You can create your own event handler to log db-ally executions to any system you want.

In this guide we will implement a simple [Event Handler](../reference/event_handlers/index.md) that logs every execution to a separate file.


## Implementing FileEventHandler

First, we need to create a new class that inherits from `EventHandler` and implements the all abstract methods.

```python
from dbally.audit import EventHandler, RequestStart, RequestEnd

class FileEventHandler(EventHandler):

    async def request_start(self, user_request: RequestStart):
        pass

    async def event_start(self, event, request_context):
        pass

    async def event_end(self, event, request_context):
        pass

    async def request_end(self, output: RequestEnd, request_context):
        pass
```

We need a directory to store the logs. Let's create a directory called `logs` in the current working directory.
We can do so in `__init__` method of `FileEventHandler`.

```python3
from path import Path

class FileEventHandler(EventHandler):

    def __init__(self):
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
```

Now, we can implement the `request_start` method to create a new file for each request.

Additionally `request_start` method can return a context object that will be passed to next calls.
We will return the file object that we create in `request_start` method.

```python3
from datetime import datetime

class FileEventHandler(EventHandler):

    async def request_start(self, user_request: RequestStart):
        file_name = f'{datetime.now().isoformat()}.log'
        log_file = open(self.log_dir / file_name, 'w')
        log_file.write(f'Collection: {user_request.collection}\n')
        log_file.write(f'Question: {user_request.question}\n')

        return log_file
```

Next step will be to implement `event_start` and `event_end` methods to log the events to the file.

Similarly to `request_start`, `event_start` method can return a context object that will be passed to `event_end` call.
Let's return event_time from this method to measure the time taken by the event.

```python3
from datetime import datetime

class FileEventHandler(EventHandler):

    async def event_start(self, event, request_context):
        event_time = datetime.now().isoformat()
        request_context.write(f'{event}\n')
        return event_time

    async def event_end(self, event, request_context, event_context):
        end_time = datetime.now()
        elapsed_time = end_time - event_context
        request_context.write(f'Elapsed Time: {elapsed_time.microseconds} ms\n')
        request_context.write(f'{event}\n')
```

Finally, we need to implement `request_end` method to close the file.

```python3
class FileEventHandler(EventHandler):

    async def request_end(self, output: RequestEnd, request_context):
        request_context.write(f'Output: {output.result}\n')
        request_context.close()
```

### (Optional) Annotating correct context types

We can enforce the correct context types by using generic type annotations on EventHandler class.

EventHandler can be annotated like this: `EventHandler[RequestContextType, EventContextType]`.

In our scenario we have `TextIOWrapper` (file object) as request context and `datetime` as event context, so we can modify the class definition like this:

```python3
from io import TextIOWrapper
from datetime import datetime
from dbally.audit import EventHandler

class FileEventHandler(EventHandler[TextIOWrapper, datetime]):

    async def event_end(self, event, request_context: TextIOWrapper, event_context: datetime):
        ...
```

## Registering our event handler

To use our event handler, we need to pass it to the collection when creating it:

```python
import dbally
from dbally.llms.litellm import LiteLLM

my_collection = bally.create_collection(
    "collection_name",
    llm=LiteLLM(),
    event_handlers=[FileEventHandler()],
)
```

Now you can test your event handler by running a query against the collection and checking the logs directory for the log files.

