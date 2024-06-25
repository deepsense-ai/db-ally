from io import StringIO

from rich.console import Console

from dbally.audit import CLIEventHandler


class BufferEventHandler(CLIEventHandler):
    """
    This handler stores in buffer all interactions between LLM and user happening during `Collection.ask`\
    execution.

    ### Usage

    ```python
        import dbally
        from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler

        dbally.set_event_handlers([BufferEventHandler()])
        my_collection = dbally.create_collection("my_collection", llm)
    ```
    """

    def __init__(self) -> None:
        super().__init__()

        self.buffer = StringIO()
        self._console = Console(file=self.buffer, record=True)
