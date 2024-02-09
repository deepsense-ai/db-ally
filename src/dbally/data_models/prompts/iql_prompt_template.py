import json
from typing import Callable, Dict, Optional, Tuple

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
        self.chat = _check_prompt_variables(chat, {"filters", "actions", "question"})


def _convert_llm_json_response_to_iql(llm_response_json: str) -> Tuple[str, str]:
    """
    Converts LLM json response to IQL

    Args:
        llm_response_json: LLM response in JSON format

    Returns:
        A string containing IQL for filters, newline, IQL for actions

    Raises:
        UnsuppotedQueryError: When IQL generator is unable to construct a query
        with given filters and actions.
    """

    if llm_response_json == "UnsupportedQueryError":
        raise UnsupportedQueryError
    llm_response_dict = json.loads(llm_response_json)
    return llm_response_dict.get("filters"), llm_response_dict.get("actions") or ""


default_iql_template = IQLPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to API that lets you query a database:\n"
            "<FILTERS>\n{filters}\n</FILTERS>\n<ACTIONS>:\n{actions}\n</ACTIONS>"
            "You will be provided with a user question. "
            "Please suggest which filters to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            """Insert those filters into the "filter" value in the returned JSON dictionary.\n"""
            "You can also pick actions from the list above, to be performed on the query result. "
            "Place them into the `actions` value in the returned JSON dictionary.\n"
            "Return result as a JSON dictionary with keys `filters` and `actions'. It will look like this:\n"
            """\\{{"filters": "filter1(arg1) AND filter2(arg2)"\n "actions": "sort_by_id()"}}\n"""
            "Remember! Don't give any comments, just the function calls.\n"
            "You can only use the functions that were listed. "
            "If you don't know how to answer, or available functions do not allow to fulfill query, "
            "say: `UnsupportedQueryError`",
        },
        {"role": "user", "content": "{question}"},
    ),
    llm_response_parser=_convert_llm_json_response_to_iql,
    response_format={"type": "json_object"},
)
