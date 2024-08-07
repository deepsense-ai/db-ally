import ast
import typing
from typing import List, Optional, Union

from typing_extensions import TypeAlias

from dbally.exceptions import DbAllyError

IQLNode: TypeAlias = Union[ast.expr, ast.stmt]
# TODO or maybe better:
# IQLNode: TypeAlias = Union[ast.expr, ast.Expr]
# OR even use ast.AST


class IQLError(DbAllyError):
    """
    Base exception for all IQL parsing related exceptions.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
    """

    message: str
    source: str

    def __init__(self, message: str, source: str) -> None:
        super().__init__(message)
        self.source = source


class IQLSyntaxError(IQLError):
    """
    Raised when IQL syntax is invalid.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
    """

    # TODO consider using some tool for docstring inheritance
    def __init__(self, source: str) -> None:
        message = f"Syntax error in: {source}"
        super().__init__(message, source)


class IQLEmptyExpressionError(IQLError):
    """
    Raised when IQL expression is empty.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
    """

    def __init__(self, source: str) -> None:
        message = "Empty IQL expression"
        super().__init__(message, source)


class IQLMultipleExpressionsError(IQLError):
    """
    Raised when IQL contains multiple expressions.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        nodes: List of multiple ast statements.
    """

    nodes: List[ast.stmt]

    def __init__(self, nodes: List[ast.stmt], source: str) -> None:
        message = "Multiple expressions or statements in IQL are not supported"
        super().__init__(message, source)
        self.nodes = nodes


class IQLExpressionError(IQLError):
    """
    Raised when IQL expression is invalid.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    node: IQLNode

    def __init__(self, message: str, node: IQLNode, source: str) -> None:
        message = f"{message}: {source[node.col_offset : node.end_col_offset]}"
        super().__init__(message, source)
        self.node = node


class IQLNoExpressionError(IQLExpressionError):
    """
    Raised when IQL expression is not found.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    # TODO check whether the type hint for arg 'node' is correct
    def __init__(self, node: ast.stmt, source: str) -> None:
        message = "No expression found in IQL"
        super().__init__(message, node, source)


class IQLArgumentParsingError(IQLExpressionError):
    """
    Raised when an argument cannot be parsed into a valid IQL.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    def __init__(self, node: IQLNode, source: str) -> None:
        message = "Not a valid IQL argument"
        super().__init__(message, node, source)


class IQLUnsupportedSyntaxError(IQLExpressionError):
    """
    Raised when trying to parse an unsupported syntax.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    def __init__(self, node: IQLNode, source: str, context: Optional[str] = None) -> None:
        node_name = node.__class__.__name__
        message = f"{node_name} syntax is not supported in IQL"
        if context:
            message += " " + context

        super().__init__(message, node, source)


class IQLFunctionNotExists(IQLExpressionError):
    """
    Raised when IQL contains function call to a function that not exists.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    def __init__(self, node: ast.Name, source: str) -> None:
        message = f"Function {node.id} not exists"
        super().__init__(message, node, source)


class IQLIncorrectNumberArgumentsError(IQLExpressionError):
    """
    Raised when IQL contains too many arguments for a function.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """

    def __init__(self, node: ast.Call, source: str) -> None:
        # TYPING CHECK
        # normally node.func is of type ast.expr, which does not guarantee having 'id' attr
        # ast.Name does and we expect it here
        # TODO check is it possible for node.func not be of type 'ast.Name' in our case
        node_name = typing.cast(ast.Name, node.func)

        message = f"The method {node_name.id} has incorrect number of arguments"
        super().__init__(message, node, source)


class IQLArgumentValidationError(IQLExpressionError):
    """
    Raised when argument is not valid for a given method.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
    """


class IQLContextNotAllowedError(IQLExpressionError):
    """
    Raised when a context call/keyword has been passed as an argument to the filter
    which does not support contextualization for this specific parameter.

    Attributes:
        message: Error message.
        source: Raw LLM response containing IQL filter calls.
        node: IQL node which parsing caused an error.
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
