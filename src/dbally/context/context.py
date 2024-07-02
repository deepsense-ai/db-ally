import ast

from typing import Optional, Type, Sequence
from typing_extensions import Self
from pydantic import BaseModel

from dbally.context.exceptions import ContextNotAvailableError


CustomContextsList = Sequence[Type['BaseCallerContext']]  # TODO confirm the naming


class BaseCallerContext(BaseModel):
    """
    Base class for contexts that are used to pass additional knowledge about the caller environment to the filters. It is not made abstract for the convinience of IQL parsing.
    LLM will always return `BaseCallerContext()` when the context is required and this call will be later substitue by a proper subclass instance selected based on the filter method signature (type hints).
    """

    @classmethod
    def select_context(cls, contexts: Sequence[Type[Self]]) -> Type[Self]:
        if not contexts:
            raise ContextNotAvailableError("The LLM detected that the context is required to execute the query and the filter signature allows contextualization while the context was not provided.")

        # we assume here that each element of `contexts` represents a different subclass of BaseCallerContext
        return next(filter(lambda obj: isinstance(obj, cls), contexts))

    @classmethod
    def is_context_call(cls, node: ast.expr) -> bool:
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == cls.__name__
