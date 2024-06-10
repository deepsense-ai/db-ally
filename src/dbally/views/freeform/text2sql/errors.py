from typing import List

from dbally.exceptions import DbAllyError


class Text2SQLError(DbAllyError):
    """
    Exception raised when text2sql query generation fails.
    """

    def __init__(self, message: str, exceptions: List[Exception]) -> None:
        self.message = message
        self.exceptions = exceptions
        super().__init__(self.message)
