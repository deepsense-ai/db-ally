# LLMClient


`LLMClient` is an abstract class designed to interact with LLMs.

Concrete implementations for specific LLMs, like OpenAILLMClient, can be found in this section of our documentation.

It accepts parameters including the template, format, event tracker, and optional generation parameters like
frequency_penalty, max_tokens, and temperature (the full list of options is provided [here](./llm_options.md)).

It constructs a prompt using the [`PromptBuilder`](./prompt_builder.md) instance.


::: dbally.llm_client.base.LLMClient
