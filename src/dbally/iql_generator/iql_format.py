from abc import abstractmethod
from typing import Dict, List

from dbally.prompts.few_shot import FewShotExample
from dbally.views.exposed_functions import ExposedFunction


def _promptify_filters(
    filters: List[ExposedFunction],
) -> str:
    """
    Formats filters for prompt

    Args:
        filters: list of filters exposed by the view

    Returns:
        filters_for_prompt: filters formatted for prompt
    """
    filters_for_prompt = "\n".join([str(filter) for filter in filters])
    return filters_for_prompt


def _promptify_examples(
    examples: List[FewShotExample],
) -> str:
    """
    Formats examples for prompt

    Args:
        examples: a list of questions and answers

    Returns:
        examples_for_prompt: examples formatted for prompt
    """
    examples_for_prompt = "\n".join([f'Question: "{e.question}"\nAnswer: "{str(e)}"' for e in examples])
    return examples_for_prompt


class AbstractIQLInputFormatter:
    """
    Formats provided parameters to a form acceptable by IQL prompt
    """

    @abstractmethod
    def __call__(
        self,
    ) -> Dict[str, str]:
        pass


class DefaultIQLInputFormatter(AbstractIQLInputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt
    """

    def __init__(
        self,
        filters: List[ExposedFunction],
        question: str,
    ) -> None:
        self.filters = filters
        self.question = question

    def __call__(
        self,
    ) -> Dict[str, str]:
        filters_for_prompt = _promptify_filters(self.filters)
        return {
            "filters": filters_for_prompt,
            "question": self.question,
        }


class DefaultIQLFewShotInputFormatter(AbstractIQLInputFormatter):
    """
    Formats provided parameters to a form acceptable by default few-shot IQL prompt
    """

    def __init__(
        self,
        filters: List[ExposedFunction],
        examples: List[FewShotExample],
        question: str,
    ) -> None:
        self.filters = filters
        self.question = question
        self.examples = examples

    def __call__(
        self,
    ) -> Dict[str, str]:
        return {
            "filters": _promptify_filters(self.filters),
            "examples": _promptify_examples(self.examples),
            "question": self.question,
        }
