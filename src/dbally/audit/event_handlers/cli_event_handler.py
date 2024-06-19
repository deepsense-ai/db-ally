import re
from io import StringIO
from sys import stdout
from typing import Optional

try:
    from rich import print as pprint
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.text import Text

    RICH_OUTPUT = True
except ImportError:
    RICH_OUTPUT = False
    pprint = print  # type: ignore

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.events import Event, LLMEvent, RequestEnd, RequestStart, SimilarityEvent

_RICH_FORMATING_KEYWORD_SET = {"green", "orange", "grey", "bold", "cyan"}
_RICH_FORMATING_PATTERN = rf"\[.*({'|'.join(_RICH_FORMATING_KEYWORD_SET)}).*\]"


class CLIEventHandler(EventHandler):
    """
    This handler displays all interactions between LLM and user happening during `Collection.ask`\
    execution inside the terminal or store them in the given buffer.

    ### Usage

    ```python
        import dbally
        from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler

        my_collection = dbally.create_collection("my_collection", llm, event_handlers=[CLIEventHandler()])
    ```

    After using `CLIEventHandler`, during every `Collection.ask` execution you will see output similar to the one below:

    ![Example output from CLIEventHandler](../../assets/event_handler_example.png)
    """

    def __init__(self, buffer: Optional[StringIO] = None) -> None:
        super().__init__()

        self.buffer = buffer
        out = self.buffer if buffer else stdout
        self._console = Console(file=out, record=True) if RICH_OUTPUT else None

    def _print_syntax(self, content: str, lexer: Optional[str] = None) -> None:
        if self._console:
            if lexer:
                console_content = Syntax(content, lexer, word_wrap=True)
            else:
                console_content = Text.from_markup(content)
            self._console.print(console_content)
        else:
            content_without_formatting = re.sub(_RICH_FORMATING_PATTERN, "", content)
            print(content_without_formatting)

    async def request_start(self, user_request: RequestStart) -> None:
        """
        Displays information about event starting to the terminal.

        Args:
            user_request: Object containing name of collection and asked query
        """
        self._print_syntax(f"[orange3 bold]Request starts... \n[orange3 bold]MESSAGE: [grey53]{user_request.question}")
        self._print_syntax("[grey53]\n=======================================")
        self._print_syntax("[grey53]=======================================\n")

    async def event_start(self, event: Event, request_context: None) -> None:
        """
        Displays information that event has started, then all messages inside the prompt


        Args:
            event: db-ally event to be logged with all the details.
            request_context: Optional context passed from request_start method
        """

        if isinstance(event, LLMEvent):
            self._print_syntax(
                f"[cyan bold]LLM event starts... \n[cyan bold]LLM EVENT PROMPT TYPE: [grey53]{event.type}"
            )

            if isinstance(event.prompt, tuple):
                for msg in event.prompt:
                    self._print_syntax(f"\n[orange3]{msg['role']}")
                    self._print_syntax(msg["content"], "text")
            else:
                self._print_syntax(f"{event.prompt}", "text")
        elif isinstance(event, SimilarityEvent):
            self._print_syntax(
                f"[cyan bold]Similarity event starts... \n"
                f"[cyan bold]INPUT: [grey53]{event.input_value}\n"
                f"[cyan bold]STORE: [grey53]{event.store}\n"
                f"[cyan bold]FETCHER: [grey53]{event.fetcher}\n"
            )

    async def event_end(self, event: Optional[Event], request_context: None, event_context: None) -> None:
        """
        Displays the response from the LLM.

        Args:
            event: db-ally event to be logged with all the details.
            request_context: Optional context passed from request_start method
            event_context: Optional context passed from event_start method
        """
        if isinstance(event, LLMEvent):
            self._print_syntax(f"\n[green bold]RESPONSE: {event.response}")
            self._print_syntax("[grey53]\n=======================================")
            self._print_syntax("[grey53]=======================================\n")
        elif isinstance(event, SimilarityEvent):
            self._print_syntax(f"[green bold]OUTPUT: {event.output_value}")
            self._print_syntax("[grey53]\n=======================================")
            self._print_syntax("[grey53]=======================================\n")

    async def request_end(self, output: RequestEnd, request_context: Optional[dict] = None) -> None:
        """
        Displays the output of the request, namely the `results` and the `context`

        Args:
            output: The output of the request.
            request_context: Optional context passed from request_start method
        """
        self._print_syntax("[green bold]REQUEST OUTPUT:")
        self._print_syntax(f"Number of rows: {len(output.result.results)}")

        if "sql" in output.result.context:
            self._print_syntax(f"{output.result.context['sql']}", "psql")
