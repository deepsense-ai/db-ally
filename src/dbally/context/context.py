import ast
from dataclasses import dataclass
from typing import Iterable

from typing_extensions import Self, TypeAlias

from dbally.context.exceptions import ContextNotAvailableError

CustomContext: TypeAlias = "BaseCallerContext"


@dataclass
class BaseCallerContext:
    """
    Pydantic-based record class. Base class for contexts that are used to pass additional knowledge about
    the caller environment to the filters. It is not made abstract for the convinience of IQL parsing.
    LLM will always return `BaseCallerContext()` when the context is required and this call will be
    later substituted by a proper subclass instance selected based on the filter method signature (type hints).
    """

    @classmethod
    def select_context(cls, contexts: Iterable[CustomContext]) -> Self:
        """
        Typically called from a subclass of BaseCallerContext, selects a member object from `contexts` being
        an instance of the same class. Effectively provides a type dispatch mechanism, substituting the context
        class by its right instance.

        Args:
            contexts: A sequence of objects, each being an instance of a different BaseCallerContext subclass.

        Returns:
            An instance of the same BaseCallerContext subclass this method is caller from.

        Raises:
            ContextNotAvailableError: If the sequence of context objects passed as argument is empty.
        """

        if not contexts:
            raise ContextNotAvailableError(
                "The LLM detected that the context is required to execute the query +\
                and the filter signature allows contextualization while the context was not provided."
            )

        # TODO confirm whether it is possible to design a correct type hints here and skipping `type: ignore`
        return next(filter(lambda obj: isinstance(obj, cls), contexts))  # type: ignore

    @classmethod
    def is_context_call(cls, node: ast.expr) -> bool:
        """
        Verifies whether an AST node indicates context substitution.

        Args:
            node: An AST node (expression) to verify:

        Returns:
            Verification result.
        """

        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == cls.__name__
