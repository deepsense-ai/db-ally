from typing import Callable, Dict, Optional

from dbally.data_models.prompts.common_validation_utils import _check_prompt_variables
from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate


class IQLExplainerPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the IQL explanation.
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ) -> None:
        """
        Initializes IQLExplainerPromptTemplate class.

        Args:
            chat: chat format
            response_format: response format
            llm_response_parser: function to parse llm response
        """

        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"question", "filters", "actions"})


default_iql_explainer_template = IQLExplainerPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps describe a table generated by a query composed "
            "of a list of filters and actions that answers users' question. "
            "You are very intelligent and obedient.\n"
            "Your task is to provide natural language description of the table used by the logical query "
            "to the database.\n"
            "Describe the table in a way that is short and informative.\n"
            "Make your answer as short as possible and start it by infroming the user that the table is too long "
            "to be used in LLM call due to token limit.\n"
            "DON'T MENTION using a query in your answer.\n",
        },
        {
            "role": "user",
            "content": "The list of filters and actions below represents the answer to a question: {question}.\n"
            "Describe the table generated using this filters: {filters} and actions: {actions}.",
        },
    )
)
