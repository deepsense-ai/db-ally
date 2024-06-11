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
                in lambda case, it should be a single line expression (otherwise output correctness is not guaranteed)
        """
        self.question = question
        self.answer_expr = answer_expr

        if isinstance(self.answer_expr, str):
            self.answer = self.answer_expr
        else:
            expr_source = textwrap.dedent(inspect.getsource(self.answer_expr))
            expr_body = expr_source.replace("lambda:", "")
            expr_body = re.sub("\\#.*\n", "\n", expr_body, flags=re.MULTILINE)

            for m_name in answer_expr.__code__.co_names:
                expr_body = expr_body.replace(f"{answer_expr.__code__.co_freevars[0]}.{m_name}", m_name)

            self.answer = " ".join(expr_body.split()).strip().rstrip(",").replace("( ", "(").replace(" )", ")")
            if self.answer.startswith("("):
                self.answer = self.answer[1:-1]

    def __str__(self) -> str:
        return self.answer
