from ..._exceptions import DbAllyError


class LLMError(DbAllyError):
    """
    Base class for all exceptions raised by the LLMClient.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class LLMConnectionError(LLMError):
    """
    Raised when there is an error connecting to the LLM API.
    """

    def __init__(self, message: str = "Connection error.") -> None:
        super().__init__(message)


class LLMStatusError(LLMError):
    """
    Raised when an API response has a status code of 4xx or 5xx.
    """

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMResponseError(LLMError):
    """
    Raised when an API response has an invalid schema.
    """

    def __init__(self, message: str = "Data returned by API invalid for expected schema.") -> None:
        super().__init__(message)
