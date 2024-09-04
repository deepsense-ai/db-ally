# How-To: Visualize Collection

db-ally provides simple way to visualize your collection with [Gradio](https://gradio.app){target="_blank"}. The app allows you to debug your views and query data using different LLMs.

## Installation

Install `dbally` with `gradio` extra.

```bash
pip install dbally["gradio"]
```

## Run the app

Pick the collection created using `create_collection` and lunch the gradio interface.

```python
from dbally.gradio import create_gradio_interface

gradio_interface = create_gradio_interface(collection)
gradio_interface.launch()
```
Visit http://127.0.0.1:7860 to test the collection.

!!! note
    By default, the app will use LLM API key defined in environment variable depending on the LLM provider used. You can override the key in the app.

## Full Example

Access the full example on [GitHub](https://github.com/deepsense-ai/db-ally/tree/main/examples/visualize_collection.py){target="_blank"}.
