# How-To: Create Custom LLM

LLM is one of the main components of the db-ally ecosystem. It handles all interactions with the selected Large Language Model. It is used for operations like view selection, IQL generation and natural language response generation, therefore it is essential to be able to integrate with any LLM API you may encounter.

## Implementing a Custom LLM

The [`LLM`](../../reference/llms/index.md#dbally.llms.base.LLM) class is an abstract base class that provides a framework for interacting with a Large Language Model. To create a custom LLM, you need to create a subclass of [`LLM`](../../reference/llms/index.md#dbally.llms.base.LLM) and implement the required methods and properties.

Here's a step-by-step guide:

### Step 1: Define the subclass

First, define your subclass and specify the type of options it will use.

```python
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLMOptions

class MyLLM(LLM[LiteLLMOptions]):
    _options_cls = LiteLLMOptions
```

In this example we will be using [`LiteLLMOptions`](../../reference/llms/litellm.md#dbally.llms.clients.litellm.LiteLLMOptions), which contain all options supported by most popular LLM APIs. If you need a different interface, see [Customising LLM Options](#customising-llm-options) to learn how to implement it.

### Step 2: Create the custom LLM client

The [`client`](../../reference/llms/index.md#dbally.llms.base.LLM.client) property is an abstract method that must be implemented in your subclass. This property should return an instance of [`LLMClient`](../../reference/llms/index.md#dbally.llms.clients.base.LLMClient) that your LLM will use to interact with the model.

```python
class MyLLM(LLM[LiteLLMOptions]):
    _options_cls = LiteLLMOptions

    @cached_property
    def client(self) -> MyLLMClient:
        return MyLLMClient()
```

`MyLLMClient` should be a class that implements the [`LLMClient`](../../reference/llms/index.md#dbally.llms.clients.base.LLMClient) interface.

```python
from dbally.llms.clients.base import LLMClient

class MyLLMClient(LLMClient[LiteLLMOptions]):

    async def call(
        self,
        conversation: ChatFormat,
        options: LiteLLMOptions,
        event: LLMEvent,
        json_mode: bool = False,
    ) -> str:
        # Your LLM API call
```

The [`call`](../../reference/llms/index.md#dbally.llms.clients.base.LLMClient.call) method is an abstract method that must be implemented in your subclass. This method should call the LLM inference API and return the response in string format.

### Step 3: Use tokenizer to count tokens

The [`count_tokens`](../../reference/llms/index.md#dbally.llms.base.LLM.count_tokens) method is used to count the number of tokens in the prompt. You can override this method in your custom class to use the tokenizer and count tokens specifically for your model.

```python
class MyLLM(LLM[LiteLLMOptions]):

    def count_tokens(self, prompt: PromptTemplate) -> int:
        # Count tokens in the prompt in a custom way
```
!!!warning
    Incorrect token counting can cause problems in the [`NLResponder`](../../reference/nl_responder.md#dbally.nl_responder.nl_responder.NLResponder) and force the use of an explanation prompt template that is more generic and does not include specific rows from the IQL response.

## Customising LLM Options

[`LLMOptions`](../../reference/llms/index.md#dbally.llms.clients.base.LLMOptions) is a class that defines the options your LLM will use. To create a custom options, you need to create a subclass of [`LLMOptions`](../../reference/llms/index.md#dbally.llms.clients.base.LLMOptions) and define the required properties that will be passed to the [`LLMClient`](../../reference/llms/index.md#dbally.llms.clients.base.LLMClient).

```python
from dbally.llms.base import LLMOptions

@dataclass
class MyLLMOptions(LLMOptions):
    temperature: float
    max_tokens: int = 4096
```

Each property should be annotated with its type. You can also provide default values if necessary. Don't forget to update the custom LLM class signatures.

```python
class MyLLM(LLM[MyLLMOptions]):
    _options_cls = MyLLMOptions

class MyLLMClient(LLMClient[MyLLMOptions]):
    ...
```

## Using the Custom LLM

Once your subclass is defined, you can instantiate and use it with your collection like this.

```python
import dbally

llm = MyLLM("my_model", MyLLMOptions(temperature=0.5))
my_collection = dbally.create_collection("my_collection", llm)
response = await my_collection.ask("Which LLM should I use?")
```

Now your custom model powers the db-ally engine for querying structured data. Have fun!
