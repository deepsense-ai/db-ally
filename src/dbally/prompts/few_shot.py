import inspect
import textwrap
from typing import Callable, Union


class FewShotExample:
    """
    A question:answer representation for few-shot prompting
    """

    def __init__(self, question: str, answer_expr: Union[str, Callable]) -> None:
        self.question = question
        self.answer_expr = answer_expr

        if isinstance(self.answer_expr, str):
            self.parsed = self.answer_expr
        else:
            expr_source = textwrap.dedent(inspect.getsource(self.answer_expr))
            expr_body = expr_source.replace("lambda:", "")

            for m_name in answer_expr.__code__.co_names:
                expr_body = expr_body.replace(f"{answer_expr.__code__.co_freevars[0]}.{m_name}", m_name)

            self.parsed = expr_body.strip().rstrip(",")
            print(self.parsed)

    def __str__(self) -> str:
        return self.parsed
