from typing import Callable, Dict, Optional

from typing_extensions import Self

from dbally.data_models.prompts.common_validation_utils import ChatFormat, PromptTemplateError


def _check_chat_order(chat: ChatFormat) -> ChatFormat:
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

    Attributes:
        response_format: Optional argument used in the OpenAI API - used to force json output
        llm_response_parser: Function parsing the LLM response into IQL
    """

    def __init__(
        self,
        chat: ChatFormat,
        response_format: Optional[Dict[str, str]] = None,
        llm_response_parser: Callable = lambda x: x,
    ):
        self.chat: ChatFormat = _check_chat_order(chat)
        self.response_format = response_format
        self.llm_response_parser = llm_response_parser

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PromptTemplate) and self.chat == __value.chat

    def add_user_message(self, content: str) -> Self:
        """
        Add a user message to the template prompt.

        Args:
            content: Message to be added

        Returns:
            PromptTemplate with appended user message
        """
        return self.__class__((*self.chat, {"role": "user", "content": content}))

    def add_assistant_message(self, content: str) -> Self:
        """
        Add an assistant message to the template prompt.

        Args:
            content: Message to be added

        Returns:
            PromptTemplate with appended assistant message
        """
        return self.__class__((*self.chat, {"role": "assistant", "content": content}))
