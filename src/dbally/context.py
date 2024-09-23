from abc import ABC
from typing import ClassVar


class Context(ABC):
    """
    Base class for all contexts that are used to pass additional knowledge about the caller environment to the view.
    """

    type_name: ClassVar[str] = "Context"
    alias_name: ClassVar[str] = "CONTEXT"
