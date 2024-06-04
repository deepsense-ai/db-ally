# How-To: Visualize Views

There has been implemented Gradio Adapter class to create simple UI interface. It allows to display Data Preview related to Views
and execute user queries.

## Installation
```bash
pip install dbally[gradio]
```

## Create own gradio interface
Define collection with implemented views

```python
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(engine))
    collection.add(SampleText2SQLView, lambda: SampleText2SQLView(prepare_freeform_enginge()))
```

Create gradio interface
```python
    gradio_adapter = GradioAdapter()
    gradio_interface = await gradio_adapter.create_interface(collection, similarity_store_list=[country_similarity])
```

Launch the gradio interface. To publish public interface pass argument `share=True`
```python
    gradio_interface.launch()
```

The endpoint is set by gradio server by triggering python module with Gradio Adapter launch command.
Private endpoint is set to http://127.0.0.1:7860/ by default.

## Links
* [Example Gradio Interface](visualize_views_code.py)