# LLM Client

`LLMClient` is an abstract class designed to interact with LLMs. 

The main method responsible for generating text based on a given template and format is `self.text_generation`. It accepts parameters including the template, format, event tracker, and optional generation parameters like frequency_penalty, max_tokens, and temperature. It constructs a prompt using the [`PromptBuilder`](./prompt_builder.md) instance and generates text using the `self._call` method.

::: dbally.llm_client.base.LLMClient
