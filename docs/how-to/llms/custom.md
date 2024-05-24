# How-To: Create Custom LLM

LLM is one of the main components of the db-ally ecosystem. It handles all interactions with the selected Large Language Model. It is used for operations like view selection, IQL generation and natural language response generation, therefore it is essential to be able to integrate with any LLM API you may encounter.

## Implementing a Custom LLM

The `LLM` class is an abstract base class that provides a framework for interacting with a Large Language Model (LLM). To create a custom LLM, you need to create a subclass of `LLM` and implement the required methods and properties.

Here's a step-by-step guide:

### Step 1: Define the subclass

First, define your subclass and specify the type of options it will use:

```python
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLMOptions

class MyLLM(LLM[LiteLLMOptions]):
    _options_cls = LiteLLMOptions
```

In this example we will be using `LiteLLMOptions`, which contain all options supported by most popular LLM APIs. If you need a different interface, see [Customising LLM Options](#customising-llm-options) to learn how to implement it.

### Step 2: Create the custom LLM client

The `_client` property is an abstract method that must be implemented in your subclass. This property should return an instance of `LLMClient` that your LLM will use to interact with the model:

```python
class MyLLM(LLM[LiteLLMOptions]):
    _options_cls = LiteLLMOptions

    @cached_property
    def _client(self) -> MyLLMClient:
        return MyLLMClient()
```

`MyLLMClient` should be a class that implements the `LLMClient` interface.

```python
from dbally.llms.clients.base import LLMClient

class MyLLMClient(LLMClient[LiteLLMOptions]):

    async def call(
        self,
        prompt: ChatFormat,
        response_format: Optional[Dict[str, str]],
        options: LiteLLMOptions,
        event: LLMEvent,
    ) -> str:
        # Your LLM API call
```

The `call` method is an abstract method that must be implemented in your subclass. This method should call the LLM inference API and return the response.

### Step 3: Use tokenizer to count tokens

The `count_tokens` method is used to count the number of tokens in the messages. You can override this method in your custom class to use the tokenizer and count tokens specifically for your model.

```python
class MyLLM(LLM[LiteLLMOptions]):

    def count_tokens(self, messages: ChatFormat, fmt: Dict[str, str]) -> int:
        # Count tokens in the messages in a custom way
```
!!!warning
    Incorrect token counting can cause problems in the `NLResponder` and force the use of an explanation prompt template that is more generic and does not include specific rows from the IQL response.

### Step 4: Define custom prompt formatting

The `_format_prompt` method is used to apply formatting to the prompt template. You can override this method in your custom class to change how the formatting is performed.

```python
class MyLLM(LLM[LiteLLMOptions]):

    def _format_prompt(self, template: PromptTemplate, fmt: Dict[str, str]) -> ChatFormat:
        # Apply custom formatting to the prompt template
```
!!!note
    In general, implementation of this method is not required unless the LLM API does not support [OpenAI conversation formatting](https://platform.openai.com/docs/api-reference/chat/create#chat-create-messages){:target="_blank"}. If the model API expects a different format, override this method to avoid issues with inference call.

## Customising LLM Options

`LLMOptions` is a class that defines the options your LLM will use. To create a custom options, you need to create a subclass of `LLMOptions` and define the required properties that will be passed to the `LLMClient`.

```python
from dbally.llms.base import LLMOptions

@dataclass
class MyLLMOptions(LLMOptions):
    temperature: float
    max_tokens: int = 4096
```

Each property should be annotated with its type. You can also provide default values if necessary. Don't forget to update the custom LLM class signatures:

```python
class MyLLM(LLM[MyLLMOptions]):
    _options_cls = MyLLMOptions

class MyLLMClient(LLMClient[MyLLMOptions]):
    ...
```

## Using the Custom LLM

Once your subclass is defined, you can instantiate and use it with your collection like this:

```python
import dbally

llm = MyLLM("my_model", MyLLMOptions(temperature=0.5))
my_collection = dbally.create_collection("my_collection", llm)
response = await my_collection.ask("Which LLM should I use?")
```

Now your custom model powers the db-ally engine for querying structured data. Have fun!
