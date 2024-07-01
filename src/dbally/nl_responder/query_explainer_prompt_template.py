from typing import Any, Dict, List

from dbally.prompt import PromptTemplate
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat


class QueryExplainerPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        context: Dict[str, Any],
        results: List[Dict[str, Any]],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new QueryExplainerPromptFormat instance.

        Args:
            question: Question to be asked.
            context: Context of the query.
            results: List of results returned by the query.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.query = next((context.get(key) for key in ("iql", "sql", "query") if context.get(key)), question)
        self.number_of_results = len(results)


default_query_explainer_template = PromptTemplate[QueryExplainerPromptFormat](
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
