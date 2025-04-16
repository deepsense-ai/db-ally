from typing import List

from dbally.iql_generator.prompt import FILTERS_GENERATION_TEMPLATE, IQLGenerationPromptFormat
from dbally.prompt.elements import FewShotExample
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping


async def test_iql_prompt_format_default() -> None:
    prompt_format = IQLGenerationPromptFormat(
        question="Some question",
        methods=[
            ExposedFunction(
                name="filter_by_name", description="", parameters=[MethodParamWithTyping(name="name", type=List[str])]
            ),
            ExposedFunction(
                name="filter_by_city", description="", parameters=[MethodParamWithTyping(name="city", type=str)]
            ),
            ExposedFunction(
                name="filter_by_company", description="", parameters=[MethodParamWithTyping(name="company", type=str)]
            ),
        ],
        examples=[],
    )
    formatted_prompt = FILTERS_GENERATION_TEMPLATE.format_prompt(prompt_format)

    assert formatted_prompt.chat == [
        {
            "role": "system",
            "content": "You have access to an API that lets you query a database:\n\n"
            + "filter_by_name(name: List[str])\n"
            + "filter_by_city(city: str)\n"
            + "filter_by_company(company: str)\n\n"
            "Suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't return any comments, just the function calls.\n"
            "The output should look like Python function calls with positional arguments, joined by logic operators:\n"
            'some_filter("foo") AND (NOT filter2(120) OR filter3(True))\n\n'
            "DO NOT INCLUDE arguments names in your response. Only the values. Strings must be quoted.\n"
            "You MUST use only these functions:\n\n"
            + "filter_by_name(name: List[str])\n"
            + "filter_by_city(city: str)\n"
            + "filter_by_company(company: str)\n\n"
            "It is VERY IMPORTANT not to use functions other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`"""
            "This is CRUCIAL, otherwise the system will crash.",
            "is_example": False,
        },
        {"role": "user", "content": "Some question", "is_example": False},
    ]


async def test_iql_prompt_format_few_shots_injected() -> None:
    examples = [FewShotExample("q1", "a1")]
    prompt_format = IQLGenerationPromptFormat(
        question="Some question",
        methods=[
            ExposedFunction(
                name="filter_by_name", description="", parameters=[MethodParamWithTyping(name="name", type=List[str])]
            )
        ],
        examples=examples,
    )
    formatted_prompt = FILTERS_GENERATION_TEMPLATE.format_prompt(prompt_format)

    assert formatted_prompt.chat == [
        {
            "role": "system",
            "content": "You have access to an API that lets you query a database:\n\n"
            + "filter_by_name(name: List[str])\n\n"
            "Suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't return any comments, just the function calls.\n"
            "The output should look like Python function calls with positional arguments, joined by logic operators:\n"
            'some_filter("foo") AND (NOT filter2(120) OR filter3(True))\n\n'
            "DO NOT INCLUDE arguments names in your response. Only the values. Strings must be quoted.\n"
            "You MUST use only these functions:\n\n" + "filter_by_name(name: List[str])\n\n"
            "It is VERY IMPORTANT not to use functions other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY anything other than `UNSUPPORTED QUERY`"""
            "This is CRUCIAL, otherwise the system will crash.",
            "is_example": False,
        },
        {"role": "user", "content": examples[0].question, "is_example": True},
        {"role": "assistant", "content": examples[0].answer, "is_example": True},
        {"role": "user", "content": "Some question", "is_example": False},
    ]


async def test_iql_input_format_few_shot_examples_repeat_no_example_duplicates() -> None:
    examples = [FewShotExample("q1", "a1")]
    prompt_format = IQLGenerationPromptFormat(
        question="",
        methods=[],
        examples=examples,
    )
    formatted_prompt = FILTERS_GENERATION_TEMPLATE.format_prompt(prompt_format)

    assert len(formatted_prompt.chat) == len(FILTERS_GENERATION_TEMPLATE.chat) + (len(examples) * 2)
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
