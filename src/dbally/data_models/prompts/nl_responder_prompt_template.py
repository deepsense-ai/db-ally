from typing import Callable, Dict, Optional

from dbally.data_models.prompts.common_validation_utils import _check_prompt_variables
from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate


class NLResponderPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the natural response.
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ) -> None:
        """
        Initializes NLResponderPromptTemplate class.

        Args:
            chat: chat format
            response_format: response format
            llm_response_parser: function to parse llm response
        """

        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"rows", "sql", "question"})


default_nl_responder_template = NLResponderPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps answer the user's questions "
            "based on the table provided. You can transform the table into an answer to a question. "
            "You are very intelligent and obedient.\n"
            "The table ALWAYS contains full answer to a question.\n"
            "You have to use the following table:\n{rows}\n"
            "The query used to generate the table is: {sql}\n\n"
            "You will be given user question. Answer it using the table. Do not mention the table in your response.\n"
            "Remember, the table ALWAYS contains full answer to a question!",
        },
        {"role": "user", "content": "{question}"},
    )
)
