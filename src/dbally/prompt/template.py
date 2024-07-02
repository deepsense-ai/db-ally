import copy
import re
from typing import Callable, Dict, Generic, List, TypeVar

from typing_extensions import Self

from dbally.exceptions import DbAllyError
from dbally.prompt.elements import FewShotExample

ChatFormat = List[Dict[str, str]]


class PromptTemplateError(DbAllyError):
    """
    Error raised on incorrect PromptTemplate construction.
    """


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
    if len(chat) == 0:
        raise PromptTemplateError("Template should not be empty")

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


class PromptFormat:
    """
    Generic format for prompts allowing to inject few shot examples into the conversation.
    """

    def __init__(self, examples: List[FewShotExample] = None) -> None:
        """
        Constructs a new PromptFormat instance.

        Args:
            examples: List of examples to be injected into the conversation.
        """
        self.examples = examples or []


PromptFormatT = TypeVar("PromptFormatT", bound=PromptFormat)


class PromptTemplate(Generic[PromptFormatT]):
    """
    Class for prompt templates.
    """

    def __init__(
        self,
        chat: ChatFormat,
        *,
        json_mode: bool = False,
        response_parser: Callable = lambda x: x,
    ) -> None:
        """
        Constructs a new PromptTemplate instance.

        Args:
            chat: Chat-formatted conversation template.
            json_mode: Whether to enforce JSON response from LLM.
            response_parser: Function parsing the LLM response into the desired format.
        """
        self.chat: ChatFormat = _check_chat_order(chat)
        self.json_mode = json_mode
        self.response_parser = response_parser

    def __eq__(self, other: "PromptTemplate") -> bool:
        return isinstance(other, PromptTemplate) and self.chat == other.chat

    def _has_variable(self, variable: str) -> bool:
        """
        Validates a given chat to make sure it contains variables required.

        Args:
            variable: Variable to check.

        Returns:
            True if the variable is present in the chat.
        """
        for message in self.chat:
            if re.match(rf"{{{variable}}}", message["content"]):
                return True
        return False

    def format_prompt(self, prompt_format: PromptFormatT) -> Self:
        """
        Applies formatting to the prompt template chat contents.

        Args:
            prompt_format: Format to be applied to the prompt.

        Returns:
            PromptTemplate with formatted chat contents.
        """
        formatted_prompt = copy.deepcopy(self)
        formatting = dict(prompt_format.__dict__)

        if self._has_variable("examples"):
            formatting["examples"] = "\n".join(prompt_format.examples)
        else:
            formatted_prompt = formatted_prompt.clear_few_shot_messages()
            for example in prompt_format.examples:
                formatted_prompt = formatted_prompt.add_few_shot_message(example)

        formatted_prompt.chat = [
            {
                "role": message.get("role"),
                "content": message.get("content").format(**formatting),
                "is_example": message.get("is_example", False),
            }
            for message in formatted_prompt.chat
        ]
        return formatted_prompt

    def set_system_message(self, content: str) -> Self:
        """
        Sets a system message to the template prompt.

        Args:
            content: Message to be added.

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

    def clear_few_shot_messages(self) -> Self:
        """
        Removes all few-shot messages from the template prompt.

        Returns:
            PromptTemplate with few-shot messages removed.
        """
        return self.__class__(
            chat=[message for message in self.chat if not message.get("is_example")],
            json_mode=self.json_mode,
            response_parser=self.response_parser,
        )
