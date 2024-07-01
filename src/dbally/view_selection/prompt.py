from typing import Dict, List

from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat, PromptTemplate


class ViewSelectionPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        views: Dict[str, str],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new ViewSelectionPromptFormat instance.

        Args:
            question: Question to be asked.
            views: Dictionary of available view names with corresponding descriptions.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.views = "\n".join([f"{name}: {description}" for name, description in views.items()])


VIEW_SELECTION_TEMPLATE = PromptTemplate[ViewSelectionPromptFormat](
    [
        {
            "role": "system",
            "content": (
                "You are a very smart database programmer. "
                "You have access to API that lets you query a database:\n"
                "First you need to select a class to query, based on its description and the user question. "
                "You have the following classes to choose from:\n"
                "{views}\n"
                "Return only the selected view name. Don't give any comments.\n"
                "You can only use the classes that were listed. "
                "If none of the classes listed can be used to answer the user question, say `NoViewFoundError`"
            ),
        },
        {
            "role": "user",
            "content": "{question}",
        },
    ],
)
