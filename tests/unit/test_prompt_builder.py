import pytest

from dbally.prompts import PromptTemplate, PromptTemplateError
from dbally.prompts.common_validation_utils import ChatFormat
from dbally.prompts.elements import FewShotExample


@pytest.fixture()
def template() -> PromptTemplate:
    return PromptTemplate(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
        ]
    )


def test_prompt_template_formatting(template: PromptTemplate) -> None:
    formatted_prompt = template.format_prompt(
        {"question": "Example user question?"},
    )
    assert formatted_prompt.chat == [
        {"content": "You are a helpful assistant.", "role": "system"},
        {"content": "Example user question?", "role": "user"},
    ]


def test_missing_prompt_template_formatting(template: PromptTemplate) -> None:
    with pytest.raises(KeyError):
        template.format_prompt({})


def test_add_few_shots(template: PromptTemplate) -> None:
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
        PromptTemplate(chat=invalid_chat)
