from typing import List

import pytest

from dbally.iql_generator.iql_prompt_template import default_iql_template
from dbally.prompts.elements import FewShotExample
from dbally.prompts.formatters import IQLFewShotInputFormatter, IQLInputFormatter


async def test_iql_input_format_default() -> None:
    input_fmt = IQLInputFormatter([], "")

    conversation, format = input_fmt(default_iql_template)

    assert len(conversation.chat) == len(default_iql_template.chat)
    assert "filters" in format
    assert "question" in format


async def test_iql_input_format_few_shot_default() -> None:
    input_fmt = IQLFewShotInputFormatter([], [], "")

    conversation, format = input_fmt(default_iql_template)

    assert len(conversation.chat) == len(default_iql_template.chat)
    assert "filters" in format
    assert "question" in format


@pytest.mark.parametrize(
    "examples",
    [
        [],
        [FewShotExample("q1", "a1")],
    ],
)
async def test_iql_input_format_few_shot_examples_injected(examples: List[FewShotExample]) -> None:
    examples = [FewShotExample("q1", "a1")]
    input_fmt = IQLFewShotInputFormatter([], examples, "")

    conversation, format = input_fmt(default_iql_template)

    assert len(conversation.chat) == len(default_iql_template.chat) + (len(examples) * 2)
    assert "filters" in format
    assert "question" in format


async def test_iql_input_format_few_shot_examples_repeat_no_example_duplicates() -> None:
    examples = [FewShotExample("q1", "a1")]
    input_fmt = IQLFewShotInputFormatter([], examples, "q")

    conversation, _ = input_fmt(default_iql_template)

    assert len(conversation.chat) == len(default_iql_template.chat) + (len(examples) * 2)
    assert conversation.chat[1]["role"] == "user"
    assert conversation.chat[1]["content"] == examples[0].question
    assert conversation.chat[2]["role"] == "assistant"
    assert conversation.chat[2]["content"] == examples[0].answer

    conversation = conversation.add_assistant_message("response")

    conversation2, _ = input_fmt(conversation)

    assert len(conversation2.chat) == len(conversation.chat)
    assert conversation2.chat[1]["role"] == "user"
    assert conversation2.chat[1]["content"] == examples[0].question
    assert conversation2.chat[2]["role"] == "assistant"
    assert conversation2.chat[2]["content"] == examples[0].answer
