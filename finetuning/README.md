# How-To: Fine-tune IQL LLM

This section provides a step-by-step guide to fine-tuning a IQL LLM.

## Prerequisites

Before you start, install the required dependencies for fine-tuning LLMs.

```bash
pip install dbally[finetuning]
```

## Customizing the fine-tuning

You can customize various aspects of the fine-tuning by modifying the config files stored in the `finetuning/dbally_finetuning/config`.

Here is an example structure of the `config.yaml` file.
```bash
name:
defaults:
  - model: <model-name>
  - train_params: <train-params-name>
  - lora_params: <lora-params-name>
  - qlora_params: <qlora-params-name>
  - _self_

dataset: <dataset-name>

use_lora: <true/false>
use_qlora: <true/false>

output_dir: <output-directory>
seed: <random-seed>
env_file_path: <path-to-env-file>
overwrite_output_dir: <true/false>
neptune_enabled: <true/false>
```

The key sections you might want to adjust are `model`, `train_params`, `lora_params` and `qlora_params`.

### Training parameters (`train_params`)

The `train_params` section should correspond to [`TrainingArguments`](https://huggingface.co/docs/transformers/en/main_classes/trainer#transformers.TrainingArguments). These parameters control the training process, including learning rate, batch size, number of epochs, and more.

### LoRA parameters (`lora_params`)

The lora_params section should correspond to [`PeftConfig`](https://huggingface.co/docs/peft/en/package_reference/config#peft.PeftConfig). These parameters control the Low-Rank Adaptation (LoRA) configuration, which helps in fine-tuning large language models efficiently.

### QLoRA parameters (`qlora_params`)

The qlora_params section should correspond to [`BitsAndBytesConfig`](https://huggingface.co/docs/transformers/main_classes/quantization#transformers.BitsAndBytesConfig). These parameters control the Quantized LoRA (QLoRA) configuration, which allows for training and inference with quantized weights, reducing memory usage and computational requirements.

### Model configuration (`model`)
This section defines the model architecture and related parameters. Key elements to include are:

-   `name`: The name or path of the pre-trained model to fine-tune, such as "meta-llama/Meta-Llama-3-8B-Instruct".
-   `lora_target_modules`: List of model modules to which LoRA will be applied, for example, ["q_proj", "k_proj", "v_proj", "o_proj"].
-   `torch_dtype`: Data type for model parameters during training, such as bfloat16.
-   `context_length`: Maximum context length for the model, e.g., 2048.

## Using Neptune for Experiment Tracking

[Neptune](https://neptune.ai/) helps in tracking and logging your experiment metrics, parameters, and other metadata in a centralized location. To enable experiment tracking with Neptune, you need to configure the necessary environment variables.

Ensure you have the following environment variables set:

-   `NEPTUNE_API_TOKEN`: Your Neptune API token.
-   `NEPTUNE_PROJECT`: The name of your Neptune project.

You can set these variables in your environment or load them from a .env file.

## Running the Script

Execute the script from the root directory using the following command:

```bash
PYTHONPATH=finetuning python finetuning/dbally_finetuning/train.py
```

This command runs the fine-tuning process with the specified configuration, and the output will be under the specified `output_dir`.
