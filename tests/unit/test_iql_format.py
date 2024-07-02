from dbally.iql_generator.prompt import IQL_GENERATION_TEMPLATE, IQLGenerationPromptFormat
from dbally.prompt.elements import FewShotExample


async def test_iql_prompt_format_default() -> None:
    prompt_format = IQLGenerationPromptFormat(
        question="",
        filters=[],
        examples=[],
    )
    formatted_prompt = IQL_GENERATION_TEMPLATE.format_prompt(prompt_format)

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
            "is_example": False,
        },
        {"role": "user", "content": "", "is_example": False},
    ]


async def test_iql_prompt_format_few_shots_injected() -> None:
    examples = [FewShotExample("q1", "a1")]
    prompt_format = IQLGenerationPromptFormat(
        question="",
        filters=[],
        examples=examples,
    )
    formatted_prompt = IQL_GENERATION_TEMPLATE.format_prompt(prompt_format)

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
            "is_example": False,
        },
        {"role": "user", "content": examples[0].question, "is_example": True},
        {"role": "assistant", "content": examples[0].answer, "is_example": True},
        {"role": "user", "content": "", "is_example": False},
    ]


async def test_iql_input_format_few_shot_examples_repeat_no_example_duplicates() -> None:
    examples = [FewShotExample("q1", "a1")]
    prompt_format = IQLGenerationPromptFormat(
        question="",
        filters=[],
        examples=examples,
    )
    formatted_prompt = IQL_GENERATION_TEMPLATE.format_prompt(prompt_format)

    assert len(formatted_prompt.chat) == len(IQL_GENERATION_TEMPLATE.chat) + (len(examples) * 2)
    assert formatted_prompt.chat[1]["role"] == "user"
    assert formatted_prompt.chat[1]["content"] == examples[0].question
    assert formatted_prompt.chat[2]["role"] == "assistant"
    assert formatted_prompt.chat[2]["content"] == examples[0].answer

    formatted_prompt = formatted_prompt.add_assistant_message("response")

    formatted_prompt2 = formatted_prompt.format_prompt(prompt_format)

    assert len(formatted_prompt2.chat) == len(formatted_prompt.chat)
    assert formatted_prompt2.chat[1]["role"] == "user"
    assert formatted_prompt2.chat[1]["content"] == examples[0].question
    assert formatted_prompt2.chat[2]["role"] == "assistant"
    assert formatted_prompt2.chat[2]["content"] == examples[0].answer
