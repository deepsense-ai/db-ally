from typing import Callable

from dbally.prompts import ChatFormat, PromptTemplate, check_prompt_variables


class NLResponderPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant for the natural response.
    """

    def __init__(
        self,
        chat: ChatFormat,
        *,
        json_mode: bool = False,
        response_parser: Callable = lambda x: x,
    ) -> None:
        """
        Initializes NLResponderPromptTemplate class.

        Args:
            chat: chat format
            response_format: response format
            response_parser: function to parse llm response
        """

        super().__init__(chat, json_mode=json_mode, response_parser=response_parser)
        self.chat = check_prompt_variables(chat, {"rows", "question"})


default_nl_responder_template = NLResponderPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps answer the user's questions "
            "based on the table provided. You MUST use the table to answer the question. "
            "You are very intelligent and obedient.\n"
            "The table ALWAYS contains full answer to a question.\n"
            "Answer the question in a way that is easy to understand and informative.\n"
            "DON'T MENTION using a table in your answer.",
        },
        {
            "role": "user",
            "content": "The table below represents the answer to a question: {question}.\n"
            "{rows}\nAnswer the question: {question}.",
        },
    )
)
