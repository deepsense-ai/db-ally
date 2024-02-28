from typing import Optional, Union

try:
    from rich import print as pprint
    from rich.console import Console
    from rich.syntax import Syntax

    RICH_OUTPUT = True
except ImportError:
    RICH_OUTPUT = False
    # TODO: remove color tags from bare print
    pprint = print  # type: ignore

from dbally.audit.event_handlers.base import EventHandler
from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart


class CLIEventHandler(EventHandler):
    """
    CLI event handler interface.
    """

    def __init__(self) -> None:
        super().__init__()
        self._console = Console() if RICH_OUTPUT else None

    def _print_syntax(self, content: str, lexer: str) -> None:
        if self._console:
            console_content = Syntax(content, lexer, word_wrap=True)
            self._console.print(console_content)
        else:
            print(content)

    async def request_start(self, user_request: RequestStart) -> None:
        """
        Log the start of the request.

        Args:
            user_request: The start of the request.
        """

        pprint(f"[orange3 bold]Request starts... \n[orange3 bold]MESSAGE: [grey53]{user_request.question}")
        pprint("[grey53]\n=======================================")
        pprint("[grey53]=======================================\n")

    async def event_start(self, event: Union[LLMEvent], request_context: None) -> None:
        """
        Log the start of the event.

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method
        """

        if isinstance(event, LLMEvent):
            pprint(f"[cyan bold]LLM event starts... \n[cyan bold]LLM EVENT PROMPT TYPE: [grey53]{event.type}")

            if isinstance(event.prompt, tuple):
                for msg in event.prompt:
                    pprint(f"\n[orange3]{msg['role']}")
                    self._print_syntax(msg["content"], "text")
            else:
                self._print_syntax(f"{event.prompt}", "text")

    async def event_end(self, event: Union[None, LLMEvent], request_context: None, event_context: None) -> None:
        """
        Log the end of the event.`

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method
            event_context: Optional context passed from event_start method
        """

        if isinstance(event, LLMEvent):
            pprint(f"\n[green bold]RESPONSE: {event.response}")
            pprint("[grey53]\n=======================================")
            pprint("[grey53]=======================================\n")

    async def request_end(self, output: RequestEnd, request_context: Optional[dict] = None) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request. In this case - PSQL query.
            request_context: Optional context passed from request_start method
        """

        pprint("[green bold]REQUEST OUTPUT:")
        pprint(f"Number of rows: {len(output.result.results)}")
        if "sql" in output.result.context:
            self._print_syntax(f"{output.result.context['sql']}", "psql")
