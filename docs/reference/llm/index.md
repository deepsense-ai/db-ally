# LLMClient


`LLMClient` is an abstract class designed to interact with LLMs.

Concrete implementations for specific LLMs, like OpenAILLMClient, can be found in this section of our documentation.

[`LLMClient` configuration options]((./llm_options.md)) include: template, format, event tracker, and optional generation parameters like
frequency_penalty, max_tokens, and temperature.

It constructs a prompt using the [`PromptBuilder`](./prompt_builder.md) instance.


::: dbally.llm_client.base.LLMClient
