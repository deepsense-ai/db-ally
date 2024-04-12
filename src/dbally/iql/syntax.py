import sys
from dataclasses import dataclass
from typing import Any, Callable, List

if sys.version_info > (3, 10):
    from typing import TypeGuard

    IsBoolOpType = TypeGuard["BoolOp"]
    IsFunctionCallType = TypeGuard["FunctionCall"]
else:
    IsBoolOpType = bool
    IsFunctionCallType = bool


class Node:
    """
    Base class for all nodes in the IQL.
    """

    def is_bool_op(self) -> IsBoolOpType:
        """
        Checks if node is a boolean operation.

        Returns:
            True if the node is a boolean operation, otherwise False.
        """
        return isinstance(self, BoolOp)

    def is_function_call(self) -> IsFunctionCallType:
        """
        Checks if node is a function call.

        Returns:
            True if the node is a function call, otherwise False.
        """
        return isinstance(self, FunctionCall)


class BoolOp(Node):
    """
    Base class for boolean operator nodes.
    """

    def match(self, not_: Callable[["Not"], Any], and_: Callable[["And"], Any], or_: Callable[["Or"], Any]) -> Any:
        """
        Match syntax for convenient query building based on BoolOp type.

        Args:
            not_: Callable executed when node is Not
            and_: Callable executed when node is And
            or_: Callable executed when node is Or

        Returns:
            Result of chosen callable.

        Raises:
            ValueError: if node is not of any supported boolean types
        """
        if isinstance(self, Not):
            return not_(self)
        if isinstance(self, And):
            return and_(self)
        if isinstance(self, Or):
            return or_(self)

        raise ValueError(f"Unsupported BoolOp type {type(self)}")


@dataclass
class And(BoolOp):
    """
    And operator which may contain any number of children nodes.
    Returns True if all children are true.
    """

    children: List[Node]


@dataclass
class Or(BoolOp):
    """
    Or operator which may contain any number of children nodes.
    Returns True if any child is true.
    """

    children: List[Node]


@dataclass
class Not(BoolOp):
    """
    Not operator, contains only one children node.
    Inverts result of boolean operation.
    """

    child: Node


@dataclass
class FunctionCall(Node):
    """
    Represents a call to a function.
    Is composed of a function name and a list of arguments.
    """

    name: str
    arguments: List[Any]
