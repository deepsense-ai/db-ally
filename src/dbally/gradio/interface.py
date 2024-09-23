import json
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import pandas as pd

import dbally
from dbally import BaseStructuredView
from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.views.exceptions import ViewExecutionError


def create_gradio_interface(collection: Collection, *, preview_limit: Optional[int] = None) -> gr.Interface:
    """
    Creates a Gradio interface for interacting with the user collection and similarity stores.

    Args:
        collection: The collection to interact with.
        preview_limit: The maximum number of preview data records to display. Default is None.

    Returns:
        The created Gradio interface.
    """
    adapter = GradioAdapter(collection=collection, preview_limit=preview_limit)
    return adapter.create_interface()


class GradioAdapter:
    """
    Gradio adapter for the db-ally lab.
    """

    def __init__(self, collection: Collection, *, preview_limit: Optional[int] = None) -> None:
        """
        Creates the gradio adapter.

        Args:
            collection: The collection to interact with.
            preview_limit: The maximum number of preview data records to display.
        """
        self.collection = collection
        self.preview_limit = preview_limit
        self.log = self._setup_event_buffer()

    def _setup_event_buffer(self) -> StringIO:
        """
        Setup the event buffer for the gradio interface.

        Returns:
            The buffer event handler.
        """
        buffer_event_handler = None
        for handler in dbally.event_handlers:
            if isinstance(handler, BufferEventHandler):
                buffer_event_handler = handler

        if not buffer_event_handler:
            buffer_event_handler = BufferEventHandler()
            dbally.event_handlers.append(buffer_event_handler)

        return buffer_event_handler.buffer

    def _render_dataframe(self, df: pd.DataFrame, message: Optional[str] = None) -> Tuple[gr.Dataframe, gr.Label]:
        """
        Renders the dataframe and label for the gradio interface.

        Args:
            df: The dataframe to render.
            message: The message to display if the dataframe is empty.

        Returns:
            A tuple containing the dataframe and label.
        """
        return (
            gr.Dataframe(value=df, visible=not df.empty, height=325),
            gr.Label(value=message, visible=df.empty, show_label=False),
        )

    def _render_view_preview(self, view_name: str) -> Tuple[gr.Dataframe, gr.Label]:
        """
        Loads preview data for a selected view name.

        Args:
            view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe, load status text, and four None values to clean gradio fields.
        """
        data = pd.DataFrame()
        view = self.collection.get(view_name)

        if isinstance(view, BaseStructuredView):
            results = view.execute().results
            data = self._load_results_into_dataframe(results)
            if self.preview_limit is not None:
                data = data.head(self.preview_limit)

        return self._render_dataframe(data, "Preview not available")

    async def _ask_collection(
        self,
        question: str,
        model_name: str,
        api_key: str,
        return_natural_response: bool,
    ) -> Tuple[gr.Code, gr.Code, gr.Code, gr.Textbox, gr.Dataframe, gr.Label, str]:
        """
        Processes the question and returns the results.

        Args:
            question: The question to ask the collection.
            return_natural_response: Flag to indicate if the natural language shall be returned.

        Returns:
            A tuple containing the generated query context, the query results as a dataframe, and the log output.
        """
        self.log.seek(0)
        self.log.truncate(0)

        # pylint: disable=protected-access
        self.collection._llm.model_name = model_name
        if hasattr(self.collection._llm, "api_key"):
            self.collection._llm.api_key = api_key

        try:
            result = await self.collection.ask(
                question=question,
                return_natural_response=return_natural_response,
            )
        except (NoViewFoundError, ViewExecutionError):
            sql = ""
            iql_filters = ""
            iql_aggregation = ""
            retrieved_rows = pd.DataFrame()
            textual_response = ""
        else:
            sql = result.context.get("sql", "")
            iql_filters = result.context.get("iql", {}).get("filters", "")
            iql_aggregation = result.context.get("iql", {}).get("aggregation", "")
            retrieved_rows = self._load_results_into_dataframe(result.results)
            textual_response = result.textual_response or ""

        retrieved_rows, empty_retrieved_rows_warning = self._render_dataframe(retrieved_rows, "No rows retrieved")

        self.log.seek(0)
        log_content = self.log.read()

        return (
            gr.Code(value=iql_filters, visible=bool(iql_filters)),
            gr.Code(value=iql_aggregation, visible=bool(iql_aggregation)),
            gr.Code(value=sql, visible=bool(sql)),
            gr.Textbox(value=textual_response, visible=return_natural_response),
            retrieved_rows,
            empty_retrieved_rows_warning,
            log_content,
        )

    def _clear_results(self) -> Tuple[gr.Textbox, gr.Code, gr.Code, gr.Code, gr.Dataframe, gr.Label]:
        """
        Clears the results from the gradio interface.

        Returns:
            A tuple containing the cleared results.
        """
        retrieved_rows, retrieved_rows_label = self._render_dataframe(pd.DataFrame(), "No rows retrieved")
        return (
            gr.Textbox(visible=False),
            gr.Code(visible=False),
            gr.Code(visible=False),
            gr.Code(visible=False),
            retrieved_rows,
            retrieved_rows_label,
        )

    @staticmethod
    def _load_results_into_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Load the results into a pandas DataFrame. Makes sure that the results are json serializable.

        Args:
            results: The results to load into the DataFrame.

        Returns:
            The loaded DataFrame.
        """
        return pd.DataFrame(json.loads(json.dumps(results, default=str)))

    def create_interface(self) -> gr.Interface:
        """
        Creates a Gradio interface for interacting with the collection.

        Returns:
            The Gradio interface.
        """
        views = list(self.collection.list())
        selected_view = views[0] if views else None

        with gr.Blocks(title="db-ally lab") as demo:
            gr.Markdown("# 🔍 db-ally lab")

            with gr.Tab("Collection"):
                with gr.Row():
                    with gr.Column():
                        api_key = gr.Textbox(
                            label="API Key",
                            placeholder="Enter your API Key",
                            type="password",
                            interactive=bool(views),
                        )
                        model_name = gr.Textbox(
                            label="Model Name",
                            placeholder="Enter your model name",
                            value=self.collection._llm.model_name,  # pylint: disable=protected-access
                            interactive=bool(views),
                            max_lines=1,
                        )
                        question = gr.Textbox(
                            label="Question",
                            placeholder="Enter your question",
                            interactive=bool(views),
                            max_lines=1,
                        )
                        natural_language_response_checkbox = gr.Checkbox(
                            label="Use Natural Language Responder",
                            interactive=bool(views),
                        )
                        ask_button = gr.Button(
                            value="Ask",
                            variant="primary",
                            interactive=bool(views),
                        )
                        clear_button = gr.ClearButton(
                            value="Reset",
                            components=[question],
                            interactive=bool(views),
                        )

                    with gr.Column():
                        view_dropdown = gr.Dropdown(
                            label="View Preview",
                            choices=views,
                            value=selected_view,
                            interactive=bool(views),
                        )
                        if selected_view:
                            view_preview, view_preview_label = self._render_view_preview(selected_view)
                        else:
                            view_preview, view_preview_label = self._render_dataframe(
                                pd.DataFrame(), "No view selected"
                            )

                with gr.Tab("Results"):
                    natural_language_response = gr.Textbox(
                        label="Natural Language Response",
                        visible=False,
                    )

                    with gr.Row():
                        iql_fitlers_result = gr.Code(
                            label="IQL Filters Query",
                            lines=1,
                            language="python",
                            visible=False,
                        )
                        iql_aggregation_result = gr.Code(
                            label="IQL Aggreagation Query",
                            lines=1,
                            language="python",
                            visible=False,
                        )

                    sql_result = gr.Code(
                        label="SQL Query",
                        lines=3,
                        language="sql",
                        visible=False,
                    )
                    retrieved_rows = gr.Dataframe(
                        interactive=False,
                        height=325,
                        visible=False,
                    )
                    retrieved_rows_label = gr.Label(
                        value="No rows retrieved",
                        visible=True,
                        show_label=False,
                    )

                with gr.Tab("Logs"):
                    log_console = gr.Code(label="Logs", language="shell")

            with gr.Tab("Help"):
                gr.Markdown(
                    """
                    ## How to use this app:
                    1. Enter your API Key for the LLM you want to use in the provided field.
                    2. Choose the [model](https://docs.litellm.ai/docs/providers) you want to use.
                    3. Type your question in the textbox.
                    4. Click on `Ask`. The retrieval results will appear in the `Results` tab.

                    ## Learn more:
                    Want to learn more about db-ally? Check out our resources:
                    - [Website](https://deepsense.ai/db-ally)
                    - [GitHub](https://github.com/deepsense-ai/db-ally)
                    - [Documentation](https://db-ally.deepsense.ai)
                    """
                )

            clear_button.add(
                [
                    natural_language_response_checkbox,
                    natural_language_response,
                    iql_fitlers_result,
                    iql_aggregation_result,
                    sql_result,
                    retrieved_rows,
                    retrieved_rows_label,
                    log_console,
                ]
            )
            clear_button.click(
                fn=self._clear_results,
                outputs=[
                    natural_language_response,
                    iql_fitlers_result,
                    iql_aggregation_result,
                    sql_result,
                    retrieved_rows,
                    retrieved_rows_label,
                ],
            )
            view_dropdown.change(
                fn=self._render_view_preview,
                inputs=view_dropdown,
                outputs=[
                    view_preview,
                    view_preview_label,
                ],
            )
            ask_button.click(
                fn=self._ask_collection,
                inputs=[
                    question,
                    model_name,
                    api_key,
                    natural_language_response_checkbox,
                ],
                outputs=[
                    iql_fitlers_result,
                    iql_aggregation_result,
                    sql_result,
                    natural_language_response,
                    retrieved_rows,
                    retrieved_rows_label,
                    log_console,
                ],
            )

        return demo
