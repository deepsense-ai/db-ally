import copy
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple

from dbally.prompts.elements import FewShotExample
from dbally.prompts.prompt_template import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


def _promptify_filters(
    filters: List[ExposedFunction],
) -> str:
    """
    Formats filters for prompt

    Args:
        filters: list of filters exposed by the view

    Returns:
        filters formatted for prompt
    """
    filters_for_prompt = "\n".join([str(filter) for filter in filters])
    return filters_for_prompt


class InputFormatter(metaclass=ABCMeta):
    """
    Formats provided parameters to a form acceptable by IQL prompt
    """

    @abstractmethod
    def __call__(self, conversation_template: PromptTemplate) -> Tuple[PromptTemplate, Dict[str, str]]:
        """
        Runs the input formatting for provided prompt template.

        Args:
            conversation_template: a prompt template to use.

        Returns:
            A tuple with template and a dictionary with formatted inputs.
        """


class DefaultInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt
    """

    def __init__(self, filters: List[ExposedFunction], question: str) -> None:
        self.filters = filters
        self.question = question

    def __call__(self, conversation_template: PromptTemplate) -> Tuple[PromptTemplate, Dict[str, str]]:
        """
        Runs the input formatting for provided prompt template.

        Args:
            conversation_template: a prompt template to use.

        Returns:
            A tuple with template and a dictionary with formatted filters and a question.
        """
        return conversation_template, {
            "filters": _promptify_filters(self.filters),
            "question": self.question,
        }


class DefaultFewShotInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    Calling it will inject `examples` before last message in a conversation.
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

    def __call__(self, conversation_template: PromptTemplate) -> Tuple[PromptTemplate, Dict[str, str]]:
        """
        Performs a deep copy of provided template and injects examples into chat history.
        Also prepares filters and question to be included within the prompt.

        Args:
            conversation_template: a prompt template to use to inject few-shot examples.

        Returns:
            A tuple with deeply-copied and enriched with examples template
            and a dictionary with formatted filters and a question.
        """

        template_copy = copy.deepcopy(conversation_template)
        sys_msg = template_copy.chat[0]
        existing_msgs = [msg for msg in template_copy.chat[1:] if "is_example" not in msg]
        chat_examples = [
            msg
            for example in self.examples
            for msg in [
                {"role": "user", "content": example.question, "is_example": True},
                {"role": "assistant", "content": example.answer, "is_example": True},
            ]
        ]

        template_copy.chat = (
            sys_msg,
            *chat_examples,
            *existing_msgs,
        )

        return template_copy, {
            "filters": _promptify_filters(self.filters),
            "question": self.question,
        }
