from dbally.exceptions import DbAllyError
from dbally.prompts import PromptTemplate


class UnsupportedQueryError(DbAllyError):
    """
    Error raised when IQL generator is unable to construct a query
    with given filters.
    """


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


IQL_GENERATION_TEMPLATE = PromptTemplate(
    [
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
    ],
    response_parser=_validate_iql_response,
)
