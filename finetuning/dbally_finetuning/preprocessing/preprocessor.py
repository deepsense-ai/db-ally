from typing import Optional

from datasets import Dataset
from dbally_finetuning.constants import DATASET_TEXT_FIELD
from dbally_finetuning.prompt import IQL_GENERATION_TEMPLATE, IQLGenerationPromptFormat
from transformers import PreTrainedTokenizer

from dbally.prompt.template import PromptTemplate


class Preprocessor:
    """Interface for preprocessor."""

    def __init__(
        self, tokenizer: PreTrainedTokenizer, prompt_template: Optional[PromptTemplate[IQLGenerationPromptFormat]]
    ):
        self.tokenizer: PreTrainedTokenizer = tokenizer
        self._prompt_template = prompt_template or IQL_GENERATION_TEMPLATE

    def _process_example(self, example: dict):
        prompt_format = IQLGenerationPromptFormat(
            question=example["question"],
            iql_context=example["iql_context"],
            iql=example["iql"],
        )
        formatted_prompt = self._prompt_template.format_prompt(prompt_format)

        return formatted_prompt.chat

    def process(
        self,
        dataset: Dataset,
    ) -> Dataset:
        """
        Returns the dataset with the tokenized input for model.

        Args:
            dataset: Dataset.

        Returns:
            Dataset.
        """

        processed_input = [self._process_example(example) for example in dataset]

        processed_input = self.tokenizer.apply_chat_template(
            processed_input, tokenize=False, add_generation_prompt=False
        )
        return Dataset.from_dict({DATASET_TEXT_FIELD: processed_input})
