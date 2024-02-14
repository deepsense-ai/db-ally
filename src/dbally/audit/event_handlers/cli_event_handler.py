from typing import Optional, Union

from rich import print as pprint
from rich.console import Console
from rich.syntax import Syntax

from dbally.audit.event_handlers.base import EventHandler
from dbally.data_models.audit import LLMEvent, RequestEnd, RequestStart


class CLIEventHandler(EventHandler):
    """
    CLI event handler interface.
    """

    def __init__(self) -> None:
        super().__init__()
        self._console = Console()

    def _print_syntax(self, content: str, lexer: str) -> None:
        console_content = Syntax(content, lexer, word_wrap=True)
        self._console.print(console_content)

    def request_start(self, user_request: RequestStart) -> None:
        """
        Log the start of the request.

        Args:
            user_request: The start of the request.
        """

        pprint(f"[orange3 bold]Request starts... \n[orange3 bold]MESSAGE: [grey53]{user_request.question}\n")

    def event_start(self, event: Union[LLMEvent]) -> None:
        """
        Log the start of the event.

        Args:
            event: Event to be logged.
        """

        if isinstance(event, LLMEvent):
            pprint(f"[cyan bold]LLM event starts... \n[cyan bold]LLM EVENT PROMPT TYPE: [grey53]{event.type}")
            pprint("[cyan bold]PROMPT: ")
            self._print_syntax(f"{event.prompt}", "text")

    def event_end(self, event: LLMEvent, start_event_payload: Optional[dict]) -> None:
        """
        Log the end of the event.

        Args:
            event: Event to be logged.
            start_event_payload: Start event payload.
        """

        pprint(f"[green bold]RESPONSE: {event.response}")
        pprint("[grey53]\n=======================================")
        pprint("[grey53]=======================================\n")

    def request_end(self, output: RequestEnd) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request. In this case - PSQL query.
        """

        pprint("[green bold]REQUEST OUTPUT:")
        self._print_syntax(f"{output.sql}", "psql")
