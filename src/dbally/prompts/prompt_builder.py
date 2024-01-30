from typing import Dict, Optional, Union

from transformers import AutoTokenizer
from transformers.tokenization_utils import PreTrainedTokenizer

from dbally.data_models.prompt_templates import ChatFormat, PromptTemplate


class PromptBuilder:
    """Class used to build prompts"""

    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Init PromptBuilder.

        Args:
            model_name: Name of the model to load a tokenizer for.
                        Tokenizer is used to append special tokens to the prompt. If empty, no tokens will be added.
        Raises:
            OSError: If model_name is not found in huggingface.co/models
        """
        self._tokenizer: Optional[PreTrainedTokenizer] = None
        if model_name is not None:
            # openAI client handles special tokens for gpt.
            if not model_name.startswith("gpt"):
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _format_prompt(self, prompt_template: PromptTemplate, fmt: Dict[str, str]) -> PromptTemplate:
        """
        Format prompt using provided arguments

        Args:
            prompt_template: this template will be modified in place
            fmt: formatting dict

        Returns:
            PromptTemplate
        """
        for message in prompt_template.chat:
            content = message["content"].format(**fmt)
            message["content"] = content
        return prompt_template

    def build(self, prompt_template: PromptTemplate, fmt: Dict[str, str]) -> Union[str, ChatFormat]:
        """Build prompt

        Args:
            prompt_template: Prompt template in system/user/assistant openAI format.
            fmt: Dictionary with formatting.

        Returns:
            Either prompt as a string (if it was formatted for a hf model, model_name provided), or prompt as an
            openAI client style list.

        Raises:
            KeyError: If fmt does not fill all template arguments.
        """

        prompt = self._format_prompt(prompt_template, fmt).chat
        if self._tokenizer is not None:
            prompt = self._tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
        return prompt
