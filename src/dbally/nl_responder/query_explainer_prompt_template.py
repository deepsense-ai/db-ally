from typing import Callable, Dict, Optional

from dbally.prompts import ChatFormat
from dbally.prompts.common_validation_utils import _check_prompt_variables
from dbally.prompts.prompt_template import PromptTemplate


class QueryExplainerPromptTemplate(PromptTemplate):
    """
    Class for prompt templates meant to generate explanations for queries
    (when the data cannot be shown due to token limit).

        Args:
            chat: chat format
            response_format: response format
            llm_response_parser: function to parse llm response
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ) -> None:
        super().__init__(chat, response_format, llm_response_parser)
        self.chat = _check_prompt_variables(chat, {"question", "query", "number_of_results"})


default_query_explainer_template = QueryExplainerPromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps describe a table generated by a query "
            "that answers users' question. "
            "You are very intelligent and obedient.\n"
            "Your task is to provide natural language description of the table used by the logical query "
            "to the database.\n"
            "Describe the table in a way that is short and informative.\n"
            "Make your answer as short as possible, start it by infroming the user that the underlying "
            "data is too long to print and then describe the table based on the question and the query.\n"
            "DON'T MENTION using a query in your answer.\n",
        },
        {
            "role": "user",
            "content": "The query below represents the answer to a question: {question}.\n"
            "Describe the table generated using this query: {query}.\n"
            "Number of results to this query: {number_of_results}.\n",
        },
    )
)
