import sys
from dataclasses import dataclass
from typing import Any, List

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

        :returns: True if the node is a boolean operation, otherwise False.
        """
        return isinstance(self, BoolOp)

    def is_function_call(self) -> IsFunctionCallType:
        """
           Checks if node is a function call.

        :returns: True if the node is a function call, otherwise False.
        """
        return isinstance(self, FunctionCall)


class BoolOp(Node):
    """
    Base class for boolean operator nodes.
    """


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
    Represents a call to a function (filter, action).
    Is composed of a function name and a list of arguments.
    """

    name: str
    arguments: List[Any]
