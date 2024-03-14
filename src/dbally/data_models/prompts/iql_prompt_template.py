from typing import Callable, Dict, Optional

from dbally.data_models.prompts.common_validation_utils import _check_prompt_variables
from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate
from dbally.utils.errors import UnsupportedQueryError


class IQLPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the IQL
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ):
        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"filters", "question"})


def _validate_iql_response(llm_response: str) -> str:
    """
    Validates LLM response to IQL

    Args:
        llm_response: LLM response

    Returns:
        A string containing IQL for filters.

    Raises:
        UnsuppotedQueryError: When IQL generator is unable to construct a query
        with given filters.
    """

    if "unsupported query" in llm_response.lower():
        raise UnsupportedQueryError
    return llm_response


default_iql_template = IQLPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You have access to API that lets you query a database:\n"
            "\n{filters}\n"
            "Please suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't give any comments, just the function calls.\n"
            "The output will look like this:\n"
            'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n{filters}\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            """If you DON'T KNOW HOW TO ANSWER DON'T SAY \"\", SAY: `UNSUPPORTED QUERY` INSTEAD! """
            "This is CRUCIAL, otherwise the system will crash. ",
        },
        {"role": "user", "content": "{question}"},
    ),
    llm_response_parser=_validate_iql_response,
)
