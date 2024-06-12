import copy
from abc import abstractmethod
from typing import Dict, List, Tuple

from dbally.prompts.few_shot import FewShotExample
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
        filters_for_prompt: filters formatted for prompt
    """
    filters_for_prompt = "\n".join([str(filter) for filter in filters])
    return filters_for_prompt


class AbstractInputFormatter:
    """
    Formats provided parameters to a form acceptable by IQL prompt
    """

    @abstractmethod
    def __call__(self, conversation_template: PromptTemplate) -> Dict[str, str]:
        pass


class DefaultInputFormatter(AbstractInputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt
    """

    def __init__(self, filters: List[ExposedFunction], question: str) -> None:
        self.filters = filters
        self.question = question

    def __call__(self, conversation_template: PromptTemplate) -> Tuple[PromptTemplate, Dict[str, str]]:
        return conversation_template, {
            "filters": _promptify_filters(self.filters),
            "question": self.question,
        }


class DefaultFewShotInputFormatter(AbstractInputFormatter):
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
        template_copy = copy.deepcopy(conversation_template)
        sys_msg = template_copy.chat[0]
        exisiting_msgs = [c for c in template_copy.chat[1:] if "is_example" not in c]
        chat_examples = [
            c
            for e in self.examples
            for c in [
                {"role": "user", "content": e.question, "is_example": True},
                {"role": "assistant", "content": e.answer, "is_example": True},
            ]
        ]
        new_chat = (
            sys_msg,
            *chat_examples,
            *exisiting_msgs,
        )

        template_copy.chat = new_chat

        return template_copy, {
            "filters": _promptify_filters(self.filters),
            "question": self.question,
        }
