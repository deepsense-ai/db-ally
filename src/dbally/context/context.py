import ast
from abc import ABC
from typing import ClassVar, Iterable

from typing_extensions import Self

from dbally.context.exceptions import BaseContextError


class BaseCallerContext(ABC):
    """
    An interface for contexts that are used to pass additional knowledge about
    the caller environment to the filters. LLM will always return `Context()`
    when the context is required and this call will be later substituted by an instance of
    a class implementing this interface, selected based on the filter method signature (type hints).

    Attributes:
        alias: Class variable defining an alias which is defined in the prompt for the LLM to reference context.
    """

    alias: ClassVar[str] = "AskerContext"

    @classmethod
    def select_context(cls, contexts: Iterable["BaseCallerContext"]) -> Self:
        """
        Typically called from a subclass of BaseCallerContext, selects a member object from `contexts` being
        an instance of the same class. Effectively provides a type dispatch mechanism, substituting the context
        class by its right instance.

        Args:
            contexts: A sequence of objects, each being an instance of a different BaseCallerContext subclass.

        Returns:
            An instance of the same BaseCallerContext subclass this method is caller from.

        Raises:
            BaseContextError: If no element in `contexts` matches `cls` class.
        """

        try:
            selected_context = next(filter(lambda obj: isinstance(obj, cls), contexts))
        except StopIteration as e:
            # this custom exception provides more clear message what have just gone wrong
            raise BaseContextError() from e

        # TODO confirm whether it is possible to design a correct type hints here and skipping `type: ignore`
        return selected_context  # type: ignore

    @classmethod
    def is_context_call(cls, node: ast.expr) -> bool:
        """
        Verifies whether an AST node indicates context substitution.

        Args:
            node: An AST node (expression) to verify:

        Returns:
            Verification result.
        """

        return (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in [cls.alias, cls.__name__]
        )
