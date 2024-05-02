from typing import Dict, List

from typing_extensions import Self

from dbally.data_models.prompts import PromptTemplate

BASE_SYSTEM = {
    "priority": 0,
    "prompt": (
        "You are a very smart database programmer. "
        "You have access to the following {dialect} tables:\n"
        "{tables}\n"
        "Create SQL query to answer user question, with no explanation Return only SQL surrounded in"
        "```sql <QUERY> ``` block. Make sure that query is correct and executable.\n"
    ),
}

COT = {
    "priority": 1,
    "prompt": (
        "Perform following tasks:\n"
        "1. Based on the user question, rewrite the tables definition USING SAME FORMAT AS ABOVE"
        "leaving only the columns that may be useful to answer the query.\n"
        "2. Think about the solution to the task. Start thinking about what you need to do in FROM"
        "and WHERE statements to answer the question. If any complex processing is required"
        "describe it. Make this proces concise and do not generate SQL query yet\n"
        "3. Based on the user question, write the SQL query, with no explanation. Write SQL"
        "surrounded in ```sql <QUERY> ``` block. Make sure that query is correct and executable.\n"
    ),
}

FEW_SHOT = {
    "priority": 2,
    "prompt": (
        "/* Some example questions and corresponding SQL queries are provided"
        "based on similar problems : */\n {few_shot}"
    ),
}

VALUE_RETRIEVER = {"priority": 3, "prompt": ("matched values: \n" "{matched_values}")}


class FreeFormPromptBuilder:
    """This class allows to combine different prompt ingredeitnt to build a template for the FreeForm view."""

    def __init__(self):
        self.prompt_parts: List[Dict] = []

    def with_base_system(self) -> Self:
        """Adds the basic system prompt

        Returns:
            _description_
        """
        self.prompt_parts.append(BASE_SYSTEM)
        return self

    def with_cot(self) -> Self:
        """Adds the COT prompt

        Returns:
            _description_"""
        self.prompt_parts.append(COT)
        return self

    def with_few_shot(self) -> Self:
        """Adds the few-shot prompt

        Returns:
            _description_"""
        self.prompt_parts.append(FEW_SHOT)
        return self

    def build(self) -> PromptTemplate:
        """Builds the prompt template

        Returns:
            The prompt template"""
        prompt_parts_sorted = sorted(self.prompt_parts, key=lambda x: x["priority"])

        return PromptTemplate(
            chat=(
                {"role": "system", "content": "\n".join([part["prompt"] for part in prompt_parts_sorted])},
                {
                    "role": "user",
                    "content": "{question}\n. ",
                },
            ),
        )
