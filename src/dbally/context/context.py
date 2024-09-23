from abc import ABC
from typing import ClassVar


class BaseCallerContext(ABC):
    """
    An interface for contexts that are used to pass additional knowledge about
    the caller environment to the filters. LLM will always return `Context()`
    when the context is required and this call will be later substituted by an instance of
    a class implementing this interface, selected based on the filter method signature (type hints).

    Attributes:
        alias: Class variable defining an alias which is defined in the prompt for the LLM to reference context.
    """

    type_name: ClassVar[str] = "Context"
    alias_name: ClassVar[str] = "CONTEXT"
