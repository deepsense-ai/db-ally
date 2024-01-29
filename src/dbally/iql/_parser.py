import ast
from typing import Any, Union

from dbally.iql._exceptions import IQLArgumentParsingError, IQLError, IQLUnsupportedSyntaxError
from dbally.iql._syntax import IQL


class IQLParser:
    """
    Parses IQL string to tree structure.
    """

    def __init__(self, source: str):
        self.source = source

    def parse(self) -> IQL.Node:
        """
        Parse IQL string to root IQL.Node.

        :return: IQL.Node which is root of the tree representing IQL query.
        :raises IQLError: if parsing fails.
        """
        ast_tree = ast.parse(self.source)
        first_element = ast_tree.body[0]

        if not isinstance(first_element, ast.Expr):
            raise IQLError("Not a valid IQL expression", first_element, self.source)

        root = self._parse_node(first_element.value)
        return root

    def _parse_node(self, node: Union[ast.expr, ast.Expr]) -> IQL.Node:
        if isinstance(node, ast.BoolOp):
            return self._parse_bool_op(node)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return IQL.Not(self._parse_node(node.operand))
        if isinstance(node, ast.Call):
            return self._parse_call(node)

        raise IQLUnsupportedSyntaxError(node, self.source)

    def _parse_bool_op(self, node: ast.BoolOp) -> IQL.BoolOp:
        if isinstance(node.op, ast.Not):
            return IQL.Not(self._parse_node(node.values[0]))
        if isinstance(node.op, ast.And):
            return IQL.And([self._parse_node(x) for x in node.values])
        if isinstance(node.op, ast.Or):
            return IQL.Or([self._parse_node(x) for x in node.values])

        raise IQLUnsupportedSyntaxError(node, self.source, context="BoolOp")

    def _parse_call(self, node: ast.Call) -> IQL.FunctionCall:
        func = node.func

        if not isinstance(func, ast.Name):
            raise IQLUnsupportedSyntaxError(node, self.source, context="FunctionCall")

        args = []

        for arg in node.args:
            args.append(self._parse_arg(arg))

        return IQL.FunctionCall(func.id, args)

    def _parse_arg(self, arg: ast.expr) -> Any:
        if isinstance(arg, ast.List):
            return [self._parse_arg(x) for x in arg.elts]

        if not isinstance(arg, ast.Constant):
            raise IQLArgumentParsingError(arg, self.source)
        return arg.value
