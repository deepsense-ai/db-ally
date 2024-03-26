from typing import TYPE_CHECKING, Dict, Optional, Union

from dbally.data_models.prompts.prompt_template import ChatFormat, PromptTemplate

if TYPE_CHECKING:
    from transformers.tokenization_utils import PreTrainedTokenizer


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
        self._tokenizer: Optional["PreTrainedTokenizer"] = None

        if model_name is not None and not model_name.startswith("gpt"):
            try:
                from transformers import AutoTokenizer  # pylint: disable=import-outside-toplevel
            except ImportError as exc:
                raise ImportError("You need to install transformers package to use huggingface models.") from exc

            self._tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _format_prompt(self, prompt_template: PromptTemplate, fmt: Dict[str, str]) -> ChatFormat:
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

        prompt = self._format_prompt(prompt_template, fmt)
        if self._tokenizer is not None:
            prompt = self._tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
        return prompt
