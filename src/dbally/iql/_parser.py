import ast
from typing import Any, List, Union

from dbally.iql import syntax
from dbally.iql._exceptions import IQLArgumentParsingError, IQLError, IQLUnsupportedSyntaxError


class IQLParser:
    """
    Parses IQL string to tree structure.
    """

    def __init__(self, source: str):
        self.source = source

    def parse(self) -> syntax.Node:
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

    def parse_actions(self) -> List[syntax.FunctionCall]:
        """
        Parse IQL string to list of IQL actions.

        :return: list of IQL syntax.FunctionCall objects

        :raises IQLError: if parsing fails.
        """
        ast_tree = ast.parse(self.source)
        calls = []

        for element in ast_tree.body:
            if isinstance(element, ast.Expr) and isinstance(element.value, ast.Call):
                calls.append(self._parse_call(element.value))
            else:
                raise IQLError("Not a valid action", element, self.source)

        return calls

    def _parse_node(self, node: Union[ast.expr, ast.Expr]) -> syntax.Node:
        if isinstance(node, ast.BoolOp):
            return self._parse_bool_op(node)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return syntax.Not(self._parse_node(node.operand))
        if isinstance(node, ast.Call):
            return self._parse_call(node)

        raise IQLUnsupportedSyntaxError(node, self.source)

    def _parse_bool_op(self, node: ast.BoolOp) -> syntax.BoolOp:
        if isinstance(node.op, ast.Not):
            return syntax.Not(self._parse_node(node.values[0]))
        if isinstance(node.op, ast.And):
            return syntax.And([self._parse_node(x) for x in node.values])
        if isinstance(node.op, ast.Or):
            return syntax.Or([self._parse_node(x) for x in node.values])

        raise IQLUnsupportedSyntaxError(node, self.source, context="BoolOp")

    def _parse_call(self, node: ast.Call) -> syntax.FunctionCall:
        func = node.func

        if not isinstance(func, ast.Name):
            raise IQLUnsupportedSyntaxError(node, self.source, context="FunctionCall")

        args = []

        for arg in node.args:
            args.append(self._parse_arg(arg))

        return syntax.FunctionCall(func.id, args)

    def _parse_arg(self, arg: ast.expr) -> Any:
        if isinstance(arg, ast.List):
            return [self._parse_arg(x) for x in arg.elts]

        if not isinstance(arg, ast.Constant):
            raise IQLArgumentParsingError(arg, self.source)
        return arg.value
