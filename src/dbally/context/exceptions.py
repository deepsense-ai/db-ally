class BaseContextError(Exception):
    """
    A base error for context handling logic.
    """


class SuitableContextNotProvidedError(BaseContextError):
    """
    Raised when method argument type hint points that a contextualization is available
    but not suitable context was provided.
    """

    def __init__(self, filter_fun_signature: str, context_class_name: str) -> None:
        # this syntax 'or BaseCallerContext' is just to prevent type checkers
        # from raising a warning, as filter_.context_class can be None. It's essenially a fallback that should never
        # be reached, unless somebody will use this Exception against its purpose.
        # TODO consider raising a warning/error when this happens.

        message = (
            f"No context of class {context_class_name} was provided"
            f"while the filter {filter_fun_signature} requires it."
        )
        super().__init__(message)
