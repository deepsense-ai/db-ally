import inspect
import textwrap
from abc import ABC, abstractmethod
from typing import Callable, Generic, List, TypeVar, Union

TView = TypeVar("TView")  # pylint: disable=C0103


class FewShotExample(Generic[TView]):
    """
    A question:answer representation for few-shot prompting
    """

    def __init__(self, question: str, answer_expr: Union[str, Callable[[TView], None]]) -> None:
        self.question = question
        self.answer_expr = answer_expr

        if isinstance(self.answer_expr, str):
            self.parsed = self.answer_expr
        else:
            expr_source = textwrap.dedent(inspect.getsource(self.answer_expr))
            expr_body = expr_source.replace(f"lambda {answer_expr.__code__.co_varnames[0]}:", "")

            for m_name in answer_expr.__code__.co_names:
                expr_body = expr_body.replace(f"{answer_expr.__code__.co_varnames[0]}.{m_name}", m_name)

            self.parsed = expr_body.strip().rstrip(",")
            print(self.parsed)

    def __str__(self) -> str:
        return self.parsed


class AbstractFewShotSelector(Generic[TView], ABC):
    """
    Provides a selection of few-shot examples
    """

    def __init__(self, view: TView) -> None:
        self.view = view

    @abstractmethod
    def get_examples(self) -> List[FewShotExample]:
        """
        Lists all examples.

        Returns:
            List of examples
        """

    def example(self, question: str, expr: Union[str, Callable[[TView], None]]) -> FewShotExample[TView]:
        """
        Create a few-shot example with a question and a lambda (or stringified expression) describing the answer.

        Args:
            question: a question for the example
            expr: either string or a (single-line) lambda representing the answer

        Returns:
            An FewShotExample
        """
        return FewShotExample(question, expr)
