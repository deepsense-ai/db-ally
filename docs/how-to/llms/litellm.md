# How-To: Use LiteLLM models

db-ally comes with ready-to-use LLM implementation called [`LiteLLM`](../../reference/llms/litellm.md#dbally.llms.litellm.LiteLLM) that uses the litellm package under the hood, providing access to all major LLM APIs such as OpenAI, Anthropic, VertexAI, Hugging Face and more.

## Basic Usage

Install litellm extension.

```bash
pip install dbally[litellm]
```

Integrate db-ally with your LLM vendor.

=== "OpenAI"

    ```python
    import os
    from dbally.llms.litellm import LiteLLM

    ## set ENV variables
    os.environ["OPENAI_API_KEY"] = "your-api-key"

    llm=LiteLLM(model_name="gpt-4o")
    ```

=== "Anthropic"

    ```python
    import os
    from dbally.llms.litellm import LiteLLM

    ## set ENV variables
    os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

    llm=LiteLLM(model_name="claude-3-opus-20240229")
    ```

=== "Anyscale"

    ```python
    import os
    from dbally.llms.litellm import LiteLLM

    ## set ENV variables
    os.environ["ANYSCALE_API_KEY"] = "your-api-key"

    llm=LiteLLM(model_name="anyscale/meta-llama/Llama-2-70b-chat-hf")
    ```

=== "Azure OpenAI"

    ```python
    import os
    from dbally.llms.litellm import LiteLLM

    ## set ENV variables
    os.environ["AZURE_API_KEY"] = "your-api-key"
    os.environ["AZURE_API_BASE"] = "your-api-base-url"
    os.environ["AZURE_API_VERSION"] = "your-api-version"

    # optional
    os.environ["AZURE_AD_TOKEN"] = ""
    os.environ["AZURE_API_TYPE"] = ""

    llm = LiteLLM(model_name="azure/<your_deployment_name>")
    ```

Use LLM in your collection.

```python
my_collection = dbally.create_collection("my_collection", llm)
response = await my_collection.ask("Which LLM should I use?")
```

## Advanced Usage

For more advanced users, you may also want to parametrize your LLM using [`LiteLLMOptions`](../../reference/llms/litellm.md#dbally.llms.clients.litellm.LiteLLMOptions). Here is the list of availabe parameters:

- `frequency_penalty`: *number or null (optional)* - It is used to penalize new tokens based on their frequency in the text so far.

- `max_tokens`: *integer (optional)* - The maximum number of tokens to generate in the chat completion.

- `n`: *integer or null (optional)* - The number of chat completion choices to generate for each input message.

- `presence_penalty`: *number or null (optional)* - It is used to penalize new tokens based on their existence in the text so far.

- `seed`: *integer or null (optional)* - This feature is in Beta. If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed, and you should refer to the system_fingerprint response parameter to monitor changes in the backend.

- `stop`: *string/ array/ null (optional)* - Up to 4 sequences where the API will stop generating further tokens.

- `temperature`: *number or null (optional)* - The sampling temperature to be used, between 0 and 2. Higher values like 0.8 produce more random outputs, while lower values like 0.2 make outputs more focused and deterministic.

- `top_p`: *number or null (optional)* - An alternative to sampling with temperature. It instructs the model to consider the results of the tokens with top_p probability. For example, 0.1 means only the tokens comprising the top 10% probability mass are considered.

```python
import dbally

llm = MyLLM("my_model", LiteLLMOptions(temperature=0.5))
my_collection = dbally.create_collection("my_collection", llm)
```

You can also override any default parameter on [`ask`](../../reference/collection.md#dbally.Collection.ask) call.

```python
response = await my_collection.ask(
    question="Which LLM should I use?",
    llm_options=LiteLLMOptions(
        temperature=0.65,
        max_tokens=1024,
    ),
)
```

!!!warning
    Some parameters are not compatible with some models and may cause exceptions, check [LiteLLM documentation](https://docs.litellm.ai/docs/completion/input#translated-openai-params){:target="_blank"} for supported options.
