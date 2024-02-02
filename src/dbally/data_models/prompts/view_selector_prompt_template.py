import json
from typing import Callable, Dict, Optional

from dbally.data_models.prompts.common_validation_utils import _check_prompt_variables
from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate


class ViewSelectorPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the ViewSelector
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ):
        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"views"})


def _convert_llm_json_response_to_selected_view(llm_response_json: str) -> str:
    """
    Converts LLM json response to IQL

    Args:
        llm_response_json: LLM response in JSON format

    Returns:
        A string containing selected view
    """
    llm_response_dict = json.loads(llm_response_json)
    return llm_response_dict.get("view")


default_view_selector_template = ViewSelectorPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a very smart database programmer. "
            "You have access to API that lets you query a database:\n"
            "First you need to select a class to query, based on its description and the user question. "
            "You have the following classes to choose from:\n"
            "{views}\n"
            "Return only the selected view name. Don't give any comments.\n"
            "You can only use the classes that were listed. "
            "If none of the classes listed can be used to answer the user question, say `NoViewFoundError`",
        },
        {"role": "user", "content": "{question}"},
    ),
)
