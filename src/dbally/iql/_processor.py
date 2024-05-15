import ast
from typing import TYPE_CHECKING, Any, List, Optional, Union

from dbally.audit.event_tracker import EventTracker
from dbally.iql import syntax
from dbally.iql._exceptions import (
    IQLArgumentParsingError,
    IQLArgumentValidationError,
    IQLError,
    IQLFunctionNotExists,
    IQLUnsupportedSyntaxError,
)
from dbally.iql._type_validators import validate_arg_type

if TYPE_CHECKING:
    from dbally.views.structured import ExposedFunction


class IQLProcessor:
    """
    Parses IQL string to tree structure.
    """

    def __init__(
        self, source: str, allowed_functions: List["ExposedFunction"], event_tracker: Optional[EventTracker] = None
    ) -> None:
        self.source = source
        self.allowed_functions = {func.name: func for func in allowed_functions}
        self._event_tracker = event_tracker or EventTracker()

    async def process(self) -> syntax.Node:
        """
        Process IQL string to root IQL.Node.

        Returns:
            IQL.Node which is root of the tree representing IQL query.

        Raises:
             IQLError: if parsing fails.
        """
        self.source = self._to_lower_except_in_quotes(self.source, ["AND", "OR", "NOT"])

        ast_tree = ast.parse(self.source)
        first_element = ast_tree.body[0]

        if not isinstance(first_element, ast.Expr):
            raise IQLError("Not a valid IQL expression", first_element, self.source)

        root = await self._parse_node(first_element.value)
        return root

    async def _parse_node(self, node: Union[ast.expr, ast.Expr]) -> syntax.Node:
        if isinstance(node, ast.BoolOp):
            return await self._parse_bool_op(node)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return syntax.Not(await self._parse_node(node.operand))
        if isinstance(node, ast.Call):
            return await self._parse_call(node)

        raise IQLUnsupportedSyntaxError(node, self.source)

    async def _parse_bool_op(self, node: ast.BoolOp) -> syntax.BoolOp:
        if isinstance(node.op, ast.Not):
            return syntax.Not(await self._parse_node(node.values[0]))
        if isinstance(node.op, ast.And):
            return syntax.And([await self._parse_node(x) for x in node.values])
        if isinstance(node.op, ast.Or):
            return syntax.Or([await self._parse_node(x) for x in node.values])

        raise IQLUnsupportedSyntaxError(node, self.source, context="BoolOp")

    async def _parse_call(self, node: ast.Call) -> syntax.FunctionCall:
        func = node.func

        if not isinstance(func, ast.Name):
            raise IQLUnsupportedSyntaxError(node, self.source, context="FunctionCall")

        if func.id not in self.allowed_functions:
            raise IQLFunctionNotExists(func, self.source)

        func_def = self.allowed_functions[func.id]
        args = []

        if len(func_def.parameters) != len(node.args):
            raise ValueError(f"The method {func.id} has incorrect number of arguments")

        for arg, arg_def in zip(node.args, func_def.parameters):
            arg_value = self._parse_arg(arg)

            if arg_def.similarity_index:
                arg_value = await arg_def.similarity_index.similar(arg_value, event_tracker=self._event_tracker)

            check_result = validate_arg_type(arg_def.type, arg_value)

            if not check_result.valid:
                raise IQLArgumentValidationError(message=check_result.reason or "", node=arg, source=self.source)

            args.append(check_result.casted_value if check_result.casted_value is not ... else arg_value)

        return syntax.FunctionCall(func.id, args)

    def _parse_arg(self, arg: ast.expr) -> Any:
        if isinstance(arg, ast.List):
            return [self._parse_arg(x) for x in arg.elts]

        if not isinstance(arg, ast.Constant):
            raise IQLArgumentParsingError(arg, self.source)
        return arg.value

    @staticmethod
    def _to_lower_except_in_quotes(text: str, keywords: List[str]) -> str:
        """
        Scans input text for keywords and converts it to lowercase.
        Omits keyword that are contained in quotes.

        Args:
            text: input text
            keywords: list of keywords to be lowered

        Returns:
            output text with selected keywords in lowercase
        """
        inside_quotes: Union[bool, str] = False
        quote_chars = ('"', "'")
        converted_text = ""

        for c in text:
            if c in quote_chars and not inside_quotes:
                inside_quotes = c
            elif c in quote_chars and inside_quotes == c:
                inside_quotes = False

            converted_text = converted_text + c

            if inside_quotes:
                continue

            for keyword in keywords:
                last_token = converted_text[-len(keyword) :]

                if last_token == keyword:
                    converted_text = converted_text[: len(converted_text) - len(keyword)] + keyword.lower()

        return converted_text
