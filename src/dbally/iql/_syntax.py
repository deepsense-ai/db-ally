import sys
from typing import List, Any

if sys.version_info > (3, 10):
    from typing import TypeGuard
    IsBoolOpType = TypeGuard['IQL.BoolOp']
    IsFunctionCallType = TypeGuard['IQL.FunctionCall']
else:
    IsBoolOpType = bool
    IsFunctionCallType = bool


class IQL:
    """
    Intermediate Query Language definition.
    All the IQL syntax is defined in this class.
    """

    class Node:
        """
        Base class for all nodes in the IQL.
        """

        def is_bool_op(self) -> IsBoolOpType:
            return isinstance(self, IQL.BoolOp)

        def is_function_call(self) -> IsFunctionCallType:
            return isinstance(self, IQL.FunctionCall)

    class BoolOp(Node):
        """
        Base class for boolean operator nodes.
        """
        pass

    class And(BoolOp):
        """
        And operator which may contain any number of children nodes.
        Returns True if all children are true.
        """
        children: List['IQL.Node']

        def __init__(self, children: List['IQL.Node']):
            self.children = children

    class Or(BoolOp):
        """
        Or operator which may contain any number of children nodes.
        Returns True if any child is true.
        """
        children: List['IQL.Node']

        def __init__(self, children: List['IQL.Node']):
            self.children = children

    class Not(BoolOp):
        """
        Not operator, contains only one children node.
        Inverts result of boolean operation.
        """
        child: 'IQL.Node'

        def __init__(self, child: 'IQL.Node'):
            self.child = child

    class FunctionCall(Node):
        """
        Represents a call to a function (filter, action).
        Is composed of a function name and a list of arguments.
        """
        name: str
        arguments: List[Any]

        def __init__(self, name: str, arguments: List[Any]):
            self.name = name
            self.arguments = arguments
