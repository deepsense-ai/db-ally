from typing import List

import pytest

from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import ChatFormat, PromptFormat, PromptTemplate, PromptTemplateError


class QuestionPromptFormat(PromptFormat):
    """
    Generic format for prompts allowing to inject few shot examples into the conversation.
    """

    def __init__(self, question: str, examples: List[FewShotExample] = None) -> None:
        """
        Constructs a new PromptFormat instance.

        Args:
            question: Question to be asked.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question


@pytest.fixture()
def template() -> PromptTemplate[QuestionPromptFormat]:
    return PromptTemplate[QuestionPromptFormat](
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
        ]
    )


def test_prompt_template_formatting(template: PromptTemplate[QuestionPromptFormat]) -> None:
    prompt_format = QuestionPromptFormat(question="Example user question?")
    formatted_prompt = template.format_prompt(prompt_format)
    assert formatted_prompt.chat == [
        {"content": "You are a helpful assistant.", "role": "system", "is_example": False},
        {"content": "Example user question?", "role": "user", "is_example": False},
    ]


def test_missing_prompt_template_formatting(template: PromptTemplate[QuestionPromptFormat]) -> None:
    prompt_format = PromptFormat()
    with pytest.raises(KeyError):
        template.format_prompt(prompt_format)


def test_add_few_shots(template: PromptTemplate[QuestionPromptFormat]) -> None:
    examples = [
        FewShotExample(
            question="What is the capital of France?",
            answer_expr="Paris",
        ),
        FewShotExample(
            question="What is the capital of Germany?",
            answer_expr="Berlin",
        ),
    ]

    for example in examples:
        template = template.add_few_shot_message(example)

    assert template.chat == [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?", "is_example": True},
        {"role": "assistant", "content": "Paris", "is_example": True},
        {"role": "user", "content": "What is the capital of Germany?", "is_example": True},
        {"role": "assistant", "content": "Berlin", "is_example": True},
        {"role": "user", "content": "{question}"},
    ]


@pytest.mark.parametrize(
    "invalid_chat",
    [
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
            {"role": "user", "content": "{question}"},
        ],
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "{question}"},
            {"role": "assistant", "content": "{question}"},
        ],
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
            {"role": "assistant", "content": "{question}"},
            {"role": "system", "content": "{question}"},
        ],
    ],
)
def test_chat_order_validation(invalid_chat: ChatFormat) -> None:
    with pytest.raises(PromptTemplateError):
        PromptTemplate[QuestionPromptFormat](invalid_chat)
