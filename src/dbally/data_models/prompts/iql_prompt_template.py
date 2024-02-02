import json
import re
from typing import Callable, Dict, List, Optional, Set

from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate, PromptTemplateError


def _extract_variables(text: str) -> List[str]:
    """
    Given a text string, extract all variables that can be filled using .format

    Args:
        text: string to process

    Returns:
        list of variables extracted from text
    """
    pattern = r"\{([^}]+)\}"
    return re.findall(pattern, text)


def _check_prompt_variables(chat: ChatFormat, variables_to_check: Set[str]) -> ChatFormat:
    """
    Function validates a given chat to make sure it contains variables required.

    Args:
        chat: chat to validate
        variables_to_check: set of variables to assert

    Raises:
        PromptTemplateError: If required variables are missing

    Returns:
        Chat, if it's valid.
    """
    variables = []
    for message in chat:
        content = message["content"]
        variables.extend(_extract_variables(content))
    if not set(variables_to_check).issubset(variables):
        raise PromptTemplateError(
            "Cannot construct an IQL prompt template from the provided chat, "
            "because it lacks necessary string variables. "
            "The IQL chat needs to contain 'filters', 'actions' and 'question' arguments."
        )
    return chat


class IQLPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the IQL
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Optional[Callable] = None,
    ):
        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"filters", "actions", "question"})


def _convert_llm_json_response_to_iql(llm_response_json: str) -> str:
    """
    Converts LLM json response to IQL

    Args:
        llm_response_json: LLM response in JSON format

    Returns:
        A string containing IQL for filters, newline, IQL for actions
    """
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
