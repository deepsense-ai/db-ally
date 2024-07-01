import inspect
import re
import textwrap
from typing import Callable, Union


class FewShotExample:
    """
    A question:answer representation for few-shot prompting
    """

    def __init__(self, question: str, answer_expr: Union[str, Callable]) -> None:
        """
        Args:
            question: sample question
            answer_expr: it can be either a stringified expression or a lambda for greater safety and code completions.

        Raises:
            ValueError: If answer_expr is not a correct type.
        """
        self.question = question
        self.answer_expr = answer_expr

        if isinstance(self.answer_expr, str):
            self.answer = self.answer_expr
        elif callable(answer_expr):
            self.answer = self._parse_lambda(answer_expr)
        else:
            raise ValueError("Answer expression should be either a string or a lambda")

    def _parse_lambda(self, expr: Callable) -> str:
        """
        Parses provided callable in order to extract the lambda code.
        All comments and references to variables like `self` etc will be removed
        to form a simple lambda representation.

        Args:
            expr: lambda expression to parse

        Returns:
            Parsed lambda in a form of cleaned up string
        """
        # extract lambda from code
        expr_source = textwrap.dedent(inspect.getsource(expr))
        expr_body = expr_source.replace("lambda:", "")

        # clean up by removing comments, new lines, free vars (self etc)
        parsed_expr = re.sub("\\#.*\n", "\n", expr_body, flags=re.MULTILINE)

        for m_name in expr.__code__.co_names:
            parsed_expr = parsed_expr.replace(f"{expr.__code__.co_freevars[0]}.{m_name}", m_name)

        # clean up any dangling commas or leading and trailing brackets
        parsed_expr = " ".join(parsed_expr.split()).strip().rstrip(",").replace("( ", "(").replace(" )", ")")
        if parsed_expr.startswith("("):
            parsed_expr = parsed_expr[1:-1]

        return parsed_expr

    def __str__(self) -> str:
        return f"{self.question} -> {self.answer}"
