from dbally.iql_generator.iql_prompt_template import IQL_GENERATION_TEMPLATE
from dbally.prompts.elements import FewShotExample
from dbally.prompts.formatters import IQLInputFormatter


async def test_iql_input_format_default() -> None:
    formatter = IQLInputFormatter(
        question="",
        filters=[],
    )
    formatted_prompt = formatter(IQL_GENERATION_TEMPLATE)

    assert formatted_prompt.chat == [
        {
            "role": "system",
            "content": "You have access to API that lets you query a database:\n"
            "\n\n"
            "Please suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't give any comments, just the function calls.\n"
            "The output will look like this:\n"
            'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY \"\", SAY: `UNSUPPORTED QUERY` INSTEAD! """
            "This is CRUCIAL, otherwise the system will crash. ",
        },
        {"role": "user", "content": ""},
    ]


async def test_iql_input_format_few_shot_default() -> None:
    formatter = IQLInputFormatter(
        question="",
        filters=[],
        examples=[],
    )
    formatted_prompt = formatter(IQL_GENERATION_TEMPLATE)

    assert formatted_prompt.chat == [
        {
            "role": "system",
            "content": "You have access to API that lets you query a database:\n"
            "\n\n"
            "Please suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't give any comments, just the function calls.\n"
            "The output will look like this:\n"
            'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY \"\", SAY: `UNSUPPORTED QUERY` INSTEAD! """
            "This is CRUCIAL, otherwise the system will crash. ",
        },
        {"role": "user", "content": ""},
    ]


async def test_iql_input_format_few_shot_examples_injected() -> None:
    examples = [FewShotExample("q1", "a1")]
    formatter = IQLInputFormatter(
        question="",
        filters=[],
        examples=examples,
    )
    formatted_prompt = formatter(IQL_GENERATION_TEMPLATE)

    assert formatted_prompt.chat == [
        {
            "role": "system",
            "content": "You have access to API that lets you query a database:\n"
            "\n\n"
            "Please suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't give any comments, just the function calls.\n"
            "The output will look like this:\n"
            'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY \"\", SAY: `UNSUPPORTED QUERY` INSTEAD! """
            "This is CRUCIAL, otherwise the system will crash. ",
        },
        {"role": "user", "content": examples[0].question},
        {"role": "assistant", "content": examples[0].answer},
        {"role": "user", "content": ""},
    ]


async def test_iql_input_format_few_shot_examples_repeat_no_example_duplicates() -> None:
    examples = [FewShotExample("q1", "a1")]
    input_fmt = IQLInputFormatter(
        question="",
        filters=[],
        examples=examples,
    )

    conversation = input_fmt(IQL_GENERATION_TEMPLATE)

    assert len(conversation.chat) == len(IQL_GENERATION_TEMPLATE.chat) + (len(examples) * 2)
    assert conversation.chat[1]["role"] == "user"
    assert conversation.chat[1]["content"] == examples[0].question
    assert conversation.chat[2]["role"] == "assistant"
    assert conversation.chat[2]["content"] == examples[0].answer

    conversation = conversation.add_assistant_message("response")

    conversation2 = input_fmt(conversation)

    assert len(conversation2.chat) == len(conversation.chat)
    assert conversation2.chat[1]["role"] == "user"
    assert conversation2.chat[1]["content"] == examples[0].question
    assert conversation2.chat[2]["role"] == "assistant"
    assert conversation2.chat[2]["content"] == examples[0].answer
