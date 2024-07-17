# pylint: disable=C0301

from typing import List

from dbally.prompt.template import PromptFormat, PromptTemplate


class IQLGenerationPromptFormat(PromptFormat):
    """
    IQL prompt format, providing a question and filters to be used in the conversation.
    """

    def __init__(
        self,
        *,
        question: str,
        iql: str,
        iql_context: List[str],
    ) -> None:
        """
        Constructs a new IQLGenerationPromptFormat instance.

        Args:
            question: Question to be asked.
            iql: IQL.
            iql_context: List of e.g. filters or actions to be used in the prompt.
        """
        super().__init__()
        self.question = question
        self.iql_context = "\n".join([str(iql_context) for iql_context in iql_context])
        self.iql = iql


IQL_GENERATION_TEMPLATE = PromptTemplate[IQLGenerationPromptFormat](
    [
        {
            "role": "system",
            "content": "You have access to API that lets you query a database:\n"
            "\n{iql_context}\n"
            "Please suggest which one(s) to call and how they should be joined with logic operators (AND, OR, NOT).\n"
            "Remember! Don't give any comments, just the function calls.\n"
            "The output will look like this:\n"
            'filter1("arg1") AND (NOT filter2(120) OR filter3(True))\n'
            "DO NOT INCLUDE arguments names in your response. Only the values.\n"
            "You MUST use only these methods:\n"
            "\n{iql_context}\n"
            "It is VERY IMPORTANT not to use methods other than those listed above."
            "If you DON'T KNOW HOW TO ANSWER DON'T SAY \"\", SAY: `UNSUPPORTED QUERY` INSTEAD! "
            "This is CRUCIAL, otherwise the system will crash.",
        },
        {"role": "user", "content": "{question}"},
        {"role": "assistant", "content": "{iql}"},
    ]
)
