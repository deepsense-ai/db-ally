import pytest

from dbally.iql_generator.iql_prompt_template import IQLPromptTemplate
from dbally.prompts import PromptTemplateError, ChatFormat
from dbally.prompts.prompt_template import PromptTemplate
from dbally.prompts.prompt_builder import PromptBuilder


@pytest.fixture()
def simple_template():
    simple_template = PromptTemplate(
        chat=(
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
        )
    )
    return simple_template


@pytest.fixture()
def default_prompt_builder():
    builder = PromptBuilder()
    return builder


@pytest.fixture()
def hf_prompt_builder():
    builder = PromptBuilder("HuggingFaceH4/zephyr-7b-beta")
    return builder


def test_openai_client_prompt(default_prompt_builder, simple_template):
    prompt = default_prompt_builder.build(simple_template, fmt={"question": "Example user question?"})
    assert prompt == (
        {"content": "You are a helpful assistant.", "role": "system"},
        {"content": "Example user question?", "role": "user"},
    )


def test_text_prompt(hf_prompt_builder, simple_template):
    prompt = hf_prompt_builder.build(simple_template, fmt={"question": "Example user question?"})
    assert (
        prompt == "<|system|>\nYou are a helpful assistant.</s>\n<|user|>\nExample user question?</s>\n<|assistant|>\n"
    )


def test_missing_format_dict(default_prompt_builder, simple_template):
    with pytest.raises(KeyError):
        _ = default_prompt_builder.build(simple_template, fmt={})


@pytest.mark.parametrize(
    "invalid_chat",
    [
        (
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
            {"role": "user", "content": "{question}"},
        ),
        (
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "{question}"},
            {"role": "assistant", "content": "{question}"},
        ),
        (
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
            {"role": "assistant", "content": "{question}"},
            {"role": "system", "content": "{question}"},
        ),
    ],
)
def test_chat_order_validation(invalid_chat):
    with pytest.raises(PromptTemplateError):
        _ = PromptTemplate(chat=invalid_chat)


def test_dynamic_few_shot(default_prompt_builder, simple_template):
    assert (
        len(
            default_prompt_builder.build(
                simple_template.add_assistant_message("assistant message").add_user_message("user message"),
                fmt={"question": "user question"},
            )
        )
        == 4
    )


@pytest.mark.parametrize(
    "invalid_chat",
    [
        (
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
        ),
        (
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ),
        (
            {"role": "system", "content": "You are a helpful assistant. {filters}}"},
            {"role": "user", "content": "Hello"},
        ),
    ],
    ids=["Missing filters", "Missing filters, question", "Missing question"],
)
def test_bad_iql_prompt_template(invalid_chat: ChatFormat):
    with pytest.raises(PromptTemplateError):
        _ = IQLPromptTemplate(invalid_chat)


@pytest.mark.parametrize(
    "chat",
    [
        (
            {"role": "system", "content": "You are a helpful assistant.{filters}"},
            {"role": "user", "content": "{question}"},
        ),
        (
            {"role": "system", "content": "{filters}{filters}{filters}}}"},
            {"role": "user", "content": "{question}"},
        ),
    ],
    ids=["Good template", "Good template with repeating variables"],
)
def test_good_iql_prompt_template(chat: ChatFormat):
    _ = IQLPromptTemplate(chat)
