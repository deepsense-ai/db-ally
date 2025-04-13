import ast
from typing import List, Optional

from dbally.exceptions import DbAllyError


class IQLError(DbAllyError):
    """
    Base exception for all IQL parsing related exceptions.
    """

    def __init__(self, message: str, source: str) -> None:
        super().__init__(message)
        self.source = source


class IQLSyntaxError(IQLError):
    """
    Raised when IQL syntax is invalid.
    """

    def __init__(self, source: str) -> None:
        message = f"Syntax error in: {source}"
        super().__init__(message, source)


class IQLNoStatementError(IQLError):
    """
    Raised when IQL does not have any statement.
    """

    def __init__(self, source: str) -> None:
        message = "Empty IQL"
        super().__init__(message, source)


class IQLMultipleStatementsError(IQLError):
    """
    Raised when IQL contains multiple statements.
    """

    def __init__(self, nodes: List[ast.stmt], source: str) -> None:
        message = "Multiple statements in IQL are not supported"
        super().__init__(message, source)
        self.nodes = nodes


class IQLNoExpressionError(IQLError):
    """
    Raised when IQL expression is not found.
    """

    def __init__(self, node: ast.stmt, source: str) -> None:
        message = f"No expression found in IQL: {source[node.col_offset : node.end_col_offset]}"
        super().__init__(message, source)
        self.node = node


class IQLExpressionError(IQLError):
    """
    Raised when IQL expression is invalid.
    """

    def __init__(self, message: str, node: ast.expr, source: str) -> None:
        message = f"{message}: {source[node.col_offset : node.end_col_offset]}"
        super().__init__(message, source)
        self.node = node


class IQLArgumentParsingError(IQLExpressionError):
    """
    Raised when an argument cannot be parsed into a valid IQL.
    """

    def __init__(self, node: ast.expr, source: str) -> None:
        message = "Not a valid IQL argument"
        super().__init__(message, node, source)


class IQLUnsupportedSyntaxError(IQLExpressionError):
    """
    Raised when trying to parse an unsupported syntax.
    """

    def __init__(self, node: ast.expr, source: str, context: Optional[str] = None) -> None:
        message = f"{node.__class__.__name__} syntax is not supported in IQL{f' {context}' if context else ''}"
        super().__init__(message, node, source)


class IQLFunctionNotExists(IQLExpressionError):
    """
    Raised when IQL contains function call to a function that not exists.
    """

    def __init__(self, node: ast.Name, source: str) -> None:
        message = f"Function {node.id} not exists"
        super().__init__(message, node, source)


class IQLIncorrectNumberArgumentsError(IQLExpressionError):
    """
    Raised when IQL contains too many arguments for a function.
    """

    def __init__(self, node: ast.Call, source: str) -> None:
        message = f"The method {node.func.id} has incorrect number of arguments"  # type: ignore
        super().__init__(message, node, source)


class IQLArgumentValidationError(IQLExpressionError):
    """
    Raised when argument is not valid for a given method.
    """


class IQLContextError(IQLExpressionError):
    """
    Base exception for all IQL context related exceptions.
    """


class IQLContextNotAllowedError(IQLContextError):
    """
    Raised when a context keyword has been passed as an argument to the method that does not support contextualization.
    """

    def __init__(self, node: ast.Name, source: str) -> None:
        message = "The context keyword is not allowed here"
        super().__init__(message, node, source)


class IQLContextNotFoundError(IQLContextError):
    """
    Raised when a context keyword has been passed as an argument to the method that does support contextualization
    but no matching context found.
    """

    def __init__(self, node: ast.Name, source: str) -> None:
        message = "The requested context is not found"
        super().__init__(message, node, source)
