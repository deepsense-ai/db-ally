from typing import Dict, List

from typing_extensions import Self

ChatFormat = List[Dict[str, str]]


class PromptTemplateError(Exception):
    """Error raised on incorrect PromptTemplate construction"""


def check_chat_order(chat: ChatFormat) -> ChatFormat:
    """
    Pydantic validator. Checks if the chat template is constructed correctly (system, user, assistant alternating).

    Args:
        chat: Chat template

    Raises:
         PromptTemplateError: if chat template is not constructed correctly.

    Returns:
        Chat template
    """
    expected_order = ["user", "assistant"]
    for i, message in enumerate(chat):
        role = message["role"]
        if role == "system":
            if i != 0:
                raise PromptTemplateError("Only first message should come from system")
            continue
        index = i % len(expected_order)
        if role != expected_order[index - 1]:
            raise PromptTemplateError(
                "Template format is not correct. It should be system, and then user/assistant alternating."
            )

    if expected_order[index] not in ["user", "assistant"]:
        raise PromptTemplateError("Template needs to end on either user or assistant turn")
    return chat


class PromptTemplate:
    """
    Class for prompt templates
    """

    def __init__(self, chat: ChatFormat):
        self.chat = check_chat_order(chat)

    def add_user_message(self, content: str) -> Self:
        """
        Add a user message to the template prompt.

        Args:
            content: Message to be added

        Returns:
            PromptTemplate with appended user message
        """
        self.chat.append({"role": "user", "content": content})
        _ = check_chat_order(self.chat)
        return self

    def add_assistant_message(self, content: str) -> Self:
        """
        Add an assistant message to the template prompt.

        Args:
            content: Message to be added

        Returns:
            PromptTemplate with appended assistant message
        """
        self.chat.append({"role": "assistant", "content": content})
        _ = check_chat_order(self.chat)
        return self
