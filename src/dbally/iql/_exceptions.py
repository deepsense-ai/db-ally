import ast
from typing import Optional, Union

from typing_extensions import TypeAlias

from dbally.exceptions import DbAllyError

IQLNode: TypeAlias = Union[ast.stmt, ast.expr]


class IQLError(DbAllyError):
    """
    Base exception for all IQL parsing related exceptions.

    Attributes:
        node: An IQL Node (AST Exprresion) during which processing an error was encountered.
        source: Raw LLM response containing IQL filter calls.
    """

    node: IQLNode
    source: str

    def __init__(self, message: str, node: IQLNode, source: str) -> None:
        message = message + ": " + source[node.col_offset : node.end_col_offset]

        super().__init__(message)
        self.node = node
        self.source = source


class IQLArgumentParsingError(IQLError):
    """Raised when an argument cannot be parsed into a valid IQL."""

    def __init__(self, node: IQLNode, source: str) -> None:
        message = "Not a valid IQL argument"
        super().__init__(message, node, source)


class IQLUnsupportedSyntaxError(IQLError):
    """Raised when trying to parse an unsupported syntax."""

    def __init__(self, node: IQLNode, source: str, context: Optional[str] = None) -> None:
        node_name = node.__class__.__name__

        message = f"{node_name} syntax is not supported in IQL"

        if context:
            message += " " + context

        super().__init__(message, node, source)


class IQLFunctionNotExists(IQLError):
    """Raised when IQL contains function call to a function that not exists."""

    def __init__(self, node: ast.Name, source: str) -> None:
        message = f"Function {node.id} not exists"
        super().__init__(message, node, source)


class IQLArgumentValidationError(IQLError):
    """Raised when argument is not valid for a given method."""


class IQLContextNotAllowedError(IQLError):
    """
    Raised when a context call/keyword has been passed as an argument to the filter
    which does not support contextualization for this specific parameter.
    """

    def __init__(self, node: IQLNode, source: str, arg_name: Optional[str] = None) -> None:
        if arg_name is None:
            message = (
                "The LLM detected that the context is required to execute the query"
                "while the filter signature does not allow it at all."
            )
        else:
            message = (
                "The LLM detected that the context is required to execute the query"
                f"while the filter signature does allow it for `{arg_name}` argument."
            )

        super().__init__(message, node, source)
