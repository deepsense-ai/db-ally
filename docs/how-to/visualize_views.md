# How-To: Visualize Views

To create simple UI interface use [create_gradio_interface function](https://github.com/deepsense-ai/db-ally/tree/main/src/dbally/gradio/gradio_interface.py) It allows to display Data Preview related to Views
and execute user queries.

## Installation
```bash
pip install dbally["gradio"]
```
When You plan to use some other feature like faiss similarity store install them as well.

```bash
pip install dbally["faiss"]
```

## Create own gradio interface
Define collection with implemented views

```python
llm = LiteLLM(model_name="gpt-3.5-turbo")
await country_similarity.update()
collection = dbally.create_collection("recruitment", llm)
collection.add(CandidateView, lambda: CandidateView(engine))
collection.add(SampleText2SQLViewCyphers, lambda: SampleText2SQLViewCyphers(create_freeform_memory_engine()))
```

>_**NOTE**_: The following code requires environment variables to proceed with LLM queries. For the example below, set the
> ```OPENAI_API_KEY``` environment variable.

Create gradio interface
```python
gradio_interface = await create_gradio_interface(user_collection=collection)
```

Launch the gradio interface. To publish public interface pass argument `share=True`
```python
gradio_interface.launch()
```

The endpoint is set by triggering python module with Gradio Adapter launch command.
Private endpoint is set to http://127.0.0.1:7860/ by default.

## Links
* [Example Gradio Interface](https://github.com/deepsense-ai/db-ally/tree/main/examples/visualize_views_code.py)