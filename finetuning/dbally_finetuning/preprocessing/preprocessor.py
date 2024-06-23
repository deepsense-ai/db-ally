import copy
from typing import Union

from datasets import Dataset
from dbally_finetuning.constants import DATASET_TEXT_FIELD
from dbally_finetuning.data.dataset import IQLDataset, IQLExample
from transformers import PreTrainedTokenizer

from dbally.prompts import ChatFormat


class Preprocessor:
    """Interface for preprocessor."""

    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
    ):
        self.tokenizer: PreTrainedTokenizer = tokenizer

    def _process_example(
        self,
        example: IQLExample,
    ) -> Union[ChatFormat, str]:
        prompt = copy.deepcopy(example.prompt)

        if not isinstance(example.prompt, str):
            prompt.append({"role": "assistant", "content": example.iql})
        else:
            pass  # TODO

        return prompt

    def process(
        self,
        dataset: IQLDataset,
    ) -> Dataset:
        """
        Returns the dataset with the tokenized input for model.

        Args:
            dataset: IQL dataset.

        Returns:
            Dataset.
        """

        processed_input = [self._process_example(example) for example in dataset]

        processed_input = self.tokenizer.apply_chat_template(
            processed_input, tokenize=False, add_generation_prompt=False
        )
        return Dataset.from_dict({DATASET_TEXT_FIELD: processed_input})
