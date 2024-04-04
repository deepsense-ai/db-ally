# PromptBuilder

`PromptBuilder` is an abstract class designed to facilitate the construction of prompts for interaction with LLMs.

## Lifecycle

The class is initialized with an optional argument `model_name`, representing the name of the model for which a tokenizer should be loaded.

!!! tip
    To use OpenAIs' models, you do not need to provide the `model_name` argument because tokenization is performed inside the OpenAI API.

The main method used to build prompts is `self.build`.
It takes a `prompt_template` (a `ChatFormat`(#dbally.data_models.prompts.common_validation_utils.ChatFormat) object) and a formatting dictionary `fmt` as input. It formats the prompt using the `format_prompt` method. If a tokenizer is available (i.e., if `model_name` was provided during initialization), it applies the tokenizer to the formatted prompt. The method returns the formatted prompt, either as a string (if it was formatted for a Hugging Face model) or as a `ChatFormat` (`Tuple[Dict[str, str], ...]`).


::: dbally.data_models.prompts.common_validation_utils.ChatFormat
::: dbally.prompts.prompt_builder.PromptBuilder
