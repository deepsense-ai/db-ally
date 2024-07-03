# How-To: Use Local LLMs

db-ally includes a ready-to-use implementation for local LLMs called [`LocalLLM`](../../reference/llms/local.md#dbally.llms.local.LocalLLM), which leverages the Hugging Face Transformers library to provide access to various LLMs available on Hugging Face.

## Basic Usage

Install the required dependencies for using local LLMs.

```bash
pip install dbally[local]
```

Integrate db-ally with your Local LLM

First, set up your environment to use a Hugging Face model.

```python

import os
from dbally.llms.localllm import LocalLLM

os.environ["HUGGINGFACE_API_KEY"] = "your-api-key"

llm = LocalLLM(model_name="meta-llama/Meta-Llama-3-8B-Instruct")
```

Use LLM in your collection

```python

my_collection = dbally.create_collection("my_collection", llm)
response = await my_collection.ask("Which LLM should I use?")
```

## Advanced Usage

For advanced users, you can customize your LLM using [`LocalLLMOptions`](../../reference/llms/local.md#dbally.llms.clients.local.LocalLLMOptions). Here is a list of available parameters:

-   `repetition_penalty`: *float or null (optional)* - Penalizes repeated tokens to avoid repetitions.
-    `do_sample`: *bool or null (optional)* - Enables sampling instead of greedy decoding.
-    `best_of`: *int or null (optional)* - Generates multiple sequences and returns the one with the highest score.
-    `max_new_tokens`: *int (optional)* - The maximum number of new tokens to generate.
-    `top_k`: *int or null (optional)* - Limits the next token choices to the top-k probability tokens.
-    `top_p`: *float or null (optional)* - Limits the next token choices to tokens within the top-p probability mass.
-    `seed`: *int or null (optional)* - Sets the seed for random number generation to ensure reproducibility.
-    `stop_sequences`: *list of strings or null (optional)* - Specifies sequences where the generation should stop.
-    `temperature`: *float or null (optional)* - Adjusts the randomness of token selection.

```python
import dbally
from dbally.llms.clients.localllm import LocalLLMOptions

llm = LocalLLM("meta-llama/Meta-Llama-3-8B-Instruct", default_options=LocalLLMOptions(temperature=0.7))
my_collection = dbally.create_collection("my_collection", llm)
```

You can also override any default parameter on the ask [`ask`](../../reference/collection.md#dbally.Collection.ask) call.

```python
response = await my_collection.ask(
    question="Which LLM should I use?",
    llm_options=LocalLLMOptions(
        temperature=0.65,
    ),
)
```