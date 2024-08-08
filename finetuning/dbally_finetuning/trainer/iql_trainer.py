from typing import Dict, Optional

from datasets import Dataset, load_dataset
from dbally_finetuning.callbacks.neptune_callback import create_neptune_callback
from dbally_finetuning.constants import DATASET_TEXT_FIELD, DTYPES_MAPPING, DataType
from dbally_finetuning.preprocessing.preprocessor import Preprocessor
from dbally_finetuning.prompt import IQL_GENERATION_TEMPLATE
from dotenv import load_dotenv
from omegaconf import DictConfig
from peft import LoraConfig
from transformers import AutoTokenizer, BitsAndBytesConfig, PreTrainedTokenizer, TrainingArguments
from transformers.integrations import NeptuneCallback
from trl import SFTTrainer


class IQLTrainer:
    """
    IQLTrainer is responsible for setting up and managing the training of an IQL causal.
    """

    def __init__(self, config: DictConfig, output_dir: str):
        self.config: DictConfig = config
        self.output_dir = output_dir
        load_dotenv(config.env_file_path)

        self._set_tokenizer()
        self._set_processor()

        self._load_dataset()
        self._prepare_dataset()

        self._set_neptune_callback()

        self._set_trainer()

    def _load_dataset(self) -> None:
        self._dataset = load_dataset(self.config.dataset)

    def _prepare_dataset(self) -> None:
        self._processed_dataset: Dict[str, Dataset] = {}
        for split in self._dataset:
            self._processed_dataset[split] = self._processor.process(self._dataset[split])

    def _set_processor(self) -> None:
        self._processor: Preprocessor = Preprocessor(self._tokenizer, IQL_GENERATION_TEMPLATE)

    def _set_tokenizer(self) -> None:
        self._tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(self.config.model.name)
        self._tokenizer.model_max_length = self.config.model.context_length
        if self._tokenizer.pad_token_id is None:
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

    def _set_neptune_callback(self) -> None:
        if self.config.neptune_enabled:
            neptune_tags = [self.config.model.name]
            if self.config.use_lora:
                neptune_tags.append("lora")
            if self.config.use_qlora:
                neptune_tags.append("qlora")
            self.neptune_callback: Optional[NeptuneCallback] = create_neptune_callback(self.config, tags=neptune_tags)

    def _set_trainer(self) -> None:
        train_params = TrainingArguments(report_to="none", **self.config.train_params)
        torch_dtype = DTYPES_MAPPING.get(DataType(self.config.model.torch_dtype))

        peft_params: Optional[LoraConfig] = None
        qlora_params: Optional[BitsAndBytesConfig] = None

        if self.config.use_lora:
            peft_params = LoraConfig(
                target_modules=list(self.config.model.lora_target_modules), **self.config.lora_params
            )
        if self.config.use_qlora:
            qlora_params = BitsAndBytesConfig(bnb_4bit_compute_dtype=torch_dtype, **self.config.qlora_params)

        model_params = {"torch_dtype": torch_dtype, "device_map": "auto", "quantization_config": qlora_params}

        self._trainer = SFTTrainer(
            model=self.config.model.name,
            model_init_kwargs=model_params,
            args=train_params,
            train_dataset=self._processed_dataset["train"],
            eval_dataset=self._processed_dataset["test"],
            dataset_text_field=DATASET_TEXT_FIELD,
            tokenizer=self._tokenizer,
            packing=False,
            peft_config=peft_params,
            max_seq_length=self.config.model.context_length,
            callbacks=[self.neptune_callback] if self.config.neptune_enabled else [],
        )

    def finetune(self):
        """
        Initiates the fine-tuning process for the model.
        """
        self._trainer.train()
