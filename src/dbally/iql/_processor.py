import ast
from typing import Any, Iterable, List, Mapping, Optional, Union

from dbally.audit.event_tracker import EventTracker
from dbally.context._utils import _does_arg_allow_context
from dbally.context.context import BaseCallerContext, CustomContext
from dbally.context.exceptions import ContextualisationNotAllowed
from dbally.iql import syntax
from dbally.iql._exceptions import (
    IQLArgumentParsingError,
    IQLArgumentValidationError,
    IQLError,
    IQLFunctionNotExists,
    IQLUnsupportedSyntaxError,
)
from dbally.iql._type_validators import validate_arg_type
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping


class IQLProcessor:
    """
    Parses IQL string to tree structure.

    Attributes:
        source: Raw LLM response containing IQL filter calls.
        allowed_functions: A mapping (typically a dict) of all filters implemented for a certain View.
        contexts: A sequence (typically a list) of context objects, each being an instance of
            a subclass of BaseCallerContext. May contain contexts irrelevant for the currently processed query.
    """

    source: str
    allowed_functions: Mapping[str, "ExposedFunction"]
    contexts: Iterable[CustomContext]
    _event_tracker: EventTracker

    def __init__(
        self,
        source: str,
        allowed_functions: Iterable[ExposedFunction],
        contexts: Optional[Iterable[CustomContext]] = None,
        event_tracker: Optional[EventTracker] = None,
    ) -> None:
        """
        IQLProcessor class constructor.

        Args:
            source: Raw LLM response containing IQL filter calls.
            allowed_functions: An interable (typically a list) of all filters implemented for a certain View.
            contexts: An iterable (typically a list) of context objects, each being an instance of
                a subclass of BaseCallerContext.
            even_tracker: An EvenTracker instance.
        """

        self.source = source
        self.allowed_functions = {func.name: func for func in allowed_functions}
        self.contexts = contexts or []
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

        for i, (arg, arg_def) in enumerate(zip(node.args, func_def.parameters)):
            arg_value = self._parse_arg(arg, arg_spec=func_def.parameters[i], parent_func_def=func_def)

            if arg_def.similarity_index:
                arg_value = await arg_def.similarity_index.similar(arg_value, event_tracker=self._event_tracker)

            check_result = validate_arg_type(arg_def.type, arg_value)

            if not check_result.valid:
                raise IQLArgumentValidationError(message=check_result.reason or "", node=arg, source=self.source)

            args.append(check_result.casted_value if check_result.casted_value is not ... else arg_value)

        return syntax.FunctionCall(func.id, args)

    def _parse_arg(
        self,
        arg: ast.expr,
        arg_spec: Optional[MethodParamWithTyping] = None,
        parent_func_def: Optional[ExposedFunction] = None,
    ) -> Any:
        if isinstance(arg, ast.List):
            return [self._parse_arg(x) for x in arg.elts]

        if BaseCallerContext.is_context_call(arg):
            if parent_func_def is None or arg_spec is None:
                # not sure whether this line will be ever reached
                raise IQLArgumentParsingError(arg, self.source)

            if parent_func_def.context_class is None:
                raise ContextualisationNotAllowed(
                    "The LLM detected that the context is required +\
                    to execute the query while the filter signature does not allow it at all."
                )

            if not _does_arg_allow_context(arg_spec):
                raise ContextualisationNotAllowed(
                    f"The LLM detected that the context is required +\
                    to execute the query while the filter signature does allow it for `{arg_spec.name}` argument."
                )

            return parent_func_def.context_class.select_context(self.contexts)

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
