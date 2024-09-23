import ast
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from dbally.audit.event_tracker import EventTracker
from dbally.context.context import BaseCallerContext
from dbally.iql import syntax
from dbally.iql._exceptions import (
    IQLArgumentParsingError,
    IQLArgumentValidationError,
    IQLContextNotAllowedError,
    IQLContextNotFoundError,
    IQLFunctionNotExists,
    IQLIncorrectNumberArgumentsError,
    IQLMultipleStatementsError,
    IQLNoExpressionError,
    IQLNoStatementError,
    IQLSyntaxError,
    IQLUnsupportedSyntaxError,
)
from dbally.iql._type_validators import validate_arg_type
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping

RootT = TypeVar("RootT", bound=syntax.Node)


class IQLProcessor(Generic[RootT], ABC):
    """
    Base class for IQL processors.
    """

    def __init__(
        self,
        source: str,
        allowed_functions: List[ExposedFunction],
        allowed_contexts: Optional[List[BaseCallerContext]] = None,
        event_tracker: Optional[EventTracker] = None,
    ) -> None:
        self.source = source
        self.allowed_functions = {func.name: func for func in allowed_functions}
        self.contexts = {context.alias_name: context for context in allowed_contexts or []}
        self._event_tracker = event_tracker or EventTracker()

    async def process(self) -> RootT:
        """
        Process IQL string to IQL root node.

        Returns:
            IQL node which is root of the tree representing IQL query.

        Raises:
            IQLError: If parsing fails.
        """
        self.source = self._to_lower_except_in_quotes(self.source, ["AND", "OR", "NOT"])

        try:
            ast_tree = ast.parse(self.source)
        except (SyntaxError, ValueError) as exc:
            raise IQLSyntaxError(self.source) from exc

        if not ast_tree.body:
            raise IQLNoStatementError(self.source)

        if len(ast_tree.body) > 1:
            raise IQLMultipleStatementsError(ast_tree.body, self.source)

        if not isinstance(ast_tree.body[0], ast.Expr):
            raise IQLNoExpressionError(ast_tree.body[0], self.source)

        return await self._parse_node(ast_tree.body[0].value)

    @abstractmethod
    async def _parse_node(self, node: ast.expr) -> RootT:
        ...

    async def _parse_call(self, node: ast.Call) -> syntax.FunctionCall:
        if not isinstance(node.func, ast.Name):
            raise IQLUnsupportedSyntaxError(node, self.source, context="FunctionCall")

        if node.func.id not in self.allowed_functions:
            raise IQLFunctionNotExists(node.func, self.source)

        func_def = self.allowed_functions[node.func.id]

        if len(func_def.parameters) != len(node.args):
            raise IQLIncorrectNumberArgumentsError(node, self.source)

        parsed_args = await asyncio.gather(
            *[self._parse_arg(arg, arg_def) for arg, arg_def in zip(node.args, func_def.parameters)]
        )

        args = [
            self._validate_and_cast_arg(arg, arg_def, node_arg)
            for arg, arg_def, node_arg in zip(parsed_args, func_def.parameters, node.args)
        ]

        return syntax.FunctionCall(node.func.id, args)

    async def _parse_arg(self, arg: ast.expr, arg_def: MethodParamWithTyping) -> Any:
        if isinstance(arg, ast.List):
            return await asyncio.gather(*[self._parse_arg(x, arg_def) for x in arg.elts])

        if isinstance(arg, ast.Name):
            aliases = [context.alias_name for context in arg_def.contexts]

            if arg.id not in aliases:
                raise IQLContextNotAllowedError(arg, self.source)

            if context := self.contexts.get(arg.id):
                return context

            raise IQLContextNotFoundError(arg, self.source)

        if not isinstance(arg, ast.Constant):
            raise IQLArgumentParsingError(arg, self.source)

        return (
            await arg_def.similarity_index.similar(arg.value, self._event_tracker)
            if arg_def.similarity_index is not None
            else arg.value
        )

    def _validate_and_cast_arg(self, arg: Any, arg_def: MethodParamWithTyping, node: ast.expr) -> Any:
        check_result = validate_arg_type(arg_def.type, arg)
        if not check_result.valid:
            raise IQLArgumentValidationError(message=check_result.reason or "", node=node, source=self.source)
        return check_result.casted_value if check_result.casted_value is not ... else arg

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


class IQLFiltersProcessor(IQLProcessor[syntax.Node]):
    """
    IQL processor for filters.
    """

    async def _parse_node(self, node: ast.expr) -> syntax.Node:
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


class IQLAggregationProcessor(IQLProcessor[syntax.FunctionCall]):
    """
    IQL processor for aggregation.
    """

    async def _parse_node(self, node: ast.expr) -> syntax.FunctionCall:
        if isinstance(node, ast.Call):
            return await self._parse_call(node)

        raise IQLUnsupportedSyntaxError(node, self.source)
