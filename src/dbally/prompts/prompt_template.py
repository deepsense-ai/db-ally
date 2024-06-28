from typing import Callable, Dict

from typing_extensions import Self

from dbally.prompts.elements import FewShotExample

from .common_validation_utils import ChatFormat, PromptTemplateError


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
        chat: Chat-formatted template.
        json_mode: Whether to enforce JSON response from LLM.
        response_parser: Function parsing the LLM response into the desired format.
    """

    def __init__(
        self,
        chat: ChatFormat,
        *,
        json_mode: bool = False,
        response_parser: Callable = lambda x: x,
    ):
        self.chat: ChatFormat = _check_chat_order(chat)
        self.json_mode = json_mode
        self.response_parser = response_parser

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PromptTemplate) and self.chat == __value.chat

    def format_prompt(self, formatting: Dict[str, str]) -> Self:
        """
        Applies formatting to the prompt template chat contents.

        Args:
            formatting: Dictionary with formatting.

        Returns:
            PromptTemplate with formatted chat contents.
        """
        return self.__class__(
            chat=[
                {"role": message["role"], "content": message["content"].format(**formatting)} for message in self.chat
            ],
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )

    def add_system_message(self, content: str) -> Self:
        """
        Add a system message to the template prompt.

        Args:
            content: Message to be added

        Returns:
            PromptTemplate with appended system message.
        """
        return self.__class__(
            chat=[{"role": "system", "content": content}, *self.chat],
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )

    def add_user_message(self, content: str) -> Self:
        """
        Add a user message to the template prompt.

        Args:
            content: Message to be added.

        Returns:
            PromptTemplate with appended user message.
        """
        return self.__class__(
            chat=[*self.chat, {"role": "user", "content": content}],
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )

    def add_assistant_message(self, content: str) -> Self:
        """
        Add an assistant message to the template prompt.

        Args:
            content: Message to be added.

        Returns:
            PromptTemplate with appended assistant message.
        """
        return self.__class__(
            chat=[*self.chat, {"role": "assistant", "content": content}],
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )

    def add_few_shot_message(self, example: FewShotExample) -> Self:
        """
        Add a few-shot message to the template prompt.

        Args:
            example: Few-shot example to be added.

        Returns:
            PromptTemplate with appended few-shot message.

        Raises:
            PromptTemplateError: if the template is empty.
        """
        if len(self.chat) == 0:
            raise PromptTemplateError("Cannot add few-shot messages to an empty template.")

        few_shot = [
            {"role": "user", "content": example.question, "is_example": True},
            {"role": "assistant", "content": example.answer, "is_example": True},
        ]
        few_shot_index = max(
            (i for i, entry in enumerate(self.chat) if entry.get("is_example") or entry.get("role") == "system"),
            default=0,
        )
        chat = self.chat[: few_shot_index + 1] + few_shot + self.chat[few_shot_index + 1 :]

        return self.__class__(
            chat=chat,
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )
