# pylint: disable=C0301

from typing import List

from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate
from dbally.views.freeform.text2sql.config import TableConfig


class SQLGenerationPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default SQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        dialect: str,
        tables: List[TableConfig],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new SQLGenerationPromptFormat instance.

        Args:
            question: Question to be asked.
            context: Context of the query.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.dialect = dialect
        self.tables = "\n".join(table.ddl for table in tables)


SQL_GENERATION_TEMPLATE = PromptTemplate[SQLGenerationPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You are a very smart database programmer. "
                "You have access to the following {dialect} tables:\n"
                "{tables}\n"
                "Create SQL query to answer user question. Response with JSON containing following keys:\n\n"
                "- sql: SQL query to answer the question, with parameter :placeholders for user input.\n"
                "- parameters: a list of parameters to be used in the query, represented by maps with the following keys:\n"
                "  - name: the name of the parameter\n"
                "  - value: the value of the parameter\n"
                "  - table: the table the parameter is used with (if any)\n"
                "  - column: the column the parameter is compared to (if any)\n\n"
                "Respond ONLY with the raw JSON response. Don't include any additional text or characters."
            ),
        },
        {
            "role": "user",
            "content": "{question}",
        },
    ],
    json_mode=True,
)
