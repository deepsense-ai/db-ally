from typing import Dict, Union

from .common_validation_utils import ChatFormat
from .prompt_template import PromptTemplate


class PromptBuilder:
    """Class used to build prompts"""

    def format_prompt(self, prompt_template: PromptTemplate, fmt: Dict[str, str]) -> ChatFormat:
        """
        Format prompt using provided arguments

        Args:
            prompt_template: this template will be modified in place
            fmt: formatting dict

        Returns:
            ChatFormat formatted prompt
        """
        return tuple({**msg, "content": msg["content"].format(**fmt)} for msg in prompt_template.chat)

    def build(self, prompt_template: PromptTemplate, fmt: Dict[str, str]) -> Union[str, ChatFormat]:
        """Build the prompt

        Args:
            prompt_template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.

        Returns:
            Either prompt as a string (if it was formatted for a hf model, model_name provided), or prompt as an
            openAI client style list.

        Raises:
            KeyError: If fmt does not fill all template arguments.
        """

        return self.format_prompt(prompt_template, fmt)
