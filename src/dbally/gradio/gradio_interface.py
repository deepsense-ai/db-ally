# pylint: disable=too-many-locals,unused-variable
# flake8: noqa: F841

import json
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import gradio
import pandas as pd

import dbally
from dbally import BaseStructuredView
from dbally.audit.event_handlers.buffer_event_handler import BufferEventHandler
from dbally.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.views.exceptions import ViewExecutionError


def create_gradio_interface(collection: Collection, preview_limit: int = 10) -> gradio.Interface:
    """
    Creates a Gradio interface for interacting with the user collection and similarity stores.

    Args:
        collection: The collection to interact with.
        preview_limit: The maximum number of preview data records to display. Default is 10.

    Returns:
        The created Gradio interface.
    """
    adapter = GradioAdapter(collection=collection, preview_limit=preview_limit)
    return adapter.create_interface()


class GradioAdapter:
    """
    A class to adapt and integrate data collection and query execution with Gradio interface components.
    """

    def __init__(self, collection: Collection, preview_limit: int = 10) -> None:
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

    def _render_dataframe(
        self, df: pd.DataFrame, message: Optional[str] = None
    ) -> Tuple[gradio.Dataframe, gradio.Label]:
        """
        Renders the dataframe and label for the gradio interface.

        Args:
            df: The dataframe to render.
            message: The message to display if the dataframe is empty.

        Returns:
            A tuple containing the dataframe and label.
        """
        return (
            gradio.Dataframe(value=df, visible=not df.empty, height=325),
            gradio.Label(value=message, visible=df.empty, show_label=False),
        )

    def _render_view_preview(self, view_name: str) -> Tuple[gradio.Dataframe, gradio.Label]:
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
            data = data.head(self.preview_limit)

        return self._render_dataframe(data, "Preview not available")

    async def _ask_collection(
        self,
        question: str,
        return_natural_response: bool,
    ) -> Tuple[str, str, str, gradio.Text, gradio.DataFrame, str]:
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
            gradio.Code(value=iql_filters, visible=bool(iql_filters)),
            gradio.Code(value=iql_aggregation, visible=bool(iql_aggregation)),
            gradio.Code(value=sql, visible=bool(sql)),
            gradio.Textbox(value=textual_response, visible=return_natural_response),
            retrieved_rows,
            empty_retrieved_rows_warning,
            log_content,
        )

    def _clear_results(self) -> Tuple[gradio.DataFrame, gradio.Label, gradio.Text, gradio.Text]:
        """
        Clears the results from the gradio interface.

        Returns:
            A tuple containing the cleared results.
        """
        retrieved_rows, retrieved_rows_label = self._render_dataframe(pd.DataFrame(), "No rows retrieved")
        return (
            gradio.Textbox(visible=False),
            gradio.Code(visible=False),
            gradio.Code(visible=False),
            gradio.Code(visible=False),
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

    def create_interface(self) -> gradio.Interface:
        """
        Creates a Gradio interface for interacting with the collection.

        Returns:
            The Gradio interface.
        """
        view_list = [*self.collection.list()]
        if view_list:
            selected_view_name = view_list[0]
            question_interactive = True
        else:
            selected_view_name = None
            question_interactive = False

        with gradio.Blocks(title="db-ally lab") as demo:
            gradio.Markdown("# 🔍 db-ally lab")

            with gradio.Tab("Collection"):
                with gradio.Row():
                    with gradio.Column():
                        api_key = gradio.Textbox(
                            label="API Key",
                            placeholder="Enter your API Key",
                            type="password",
                            interactive=question_interactive,
                        )
                        model_name = gradio.Textbox(
                            label="Model Name",
                            placeholder="Enter your model name",
                            value="gpt-3.5-turbo",
                            interactive=question_interactive,
                            max_lines=1,
                        )
                        query = gradio.Textbox(
                            label="Question",
                            placeholder="Enter your question",
                            interactive=question_interactive,
                            max_lines=1,
                        )
                        natural_language_response_checkbox = gradio.Checkbox(
                            label="Use Natural Language Responder",
                            interactive=question_interactive,
                        )
                        query_button = gradio.Button(
                            value="Ask",
                            interactive=question_interactive,
                            variant="primary",
                        )
                        clear_button = gradio.ClearButton(
                            value="Reset",
                            components=[query],
                            interactive=question_interactive,
                        )

                    with gradio.Column():
                        view_dropdown = gradio.Dropdown(
                            label="View Preview",
                            choices=view_list,
                            value=selected_view_name,
                            interactive=question_interactive,
                        )
                        if selected_view_name:
                            view_preview, view_preview_label = self._render_view_preview(selected_view_name)
                        else:
                            view_preview, view_preview_label = self._render_dataframe(
                                pd.DataFrame(), "No view selected"
                            )

                with gradio.Tab("Logs"):
                    log_console = gradio.Code(label="Logs", language="shell")

                with gradio.Tab("Results"):
                    natural_language_response = gradio.Textbox(
                        label="Natural Language Response",
                        visible=False,
                    )

                    with gradio.Row():
                        iql_fitlers_result = gradio.Code(
                            label="IQL Filters Query",
                            lines=1,
                            language="python",
                            visible=False,
                        )
                        iql_aggregation_result = gradio.Code(
                            label="IQL Aggreagation Query",
                            lines=1,
                            language="python",
                            visible=False,
                        )

                    sql_result = gradio.Code(
                        label="SQL Query",
                        lines=3,
                        language="sql",
                        visible=False,
                    )

                    with gradio.Accordion("See Retrieved Rows", open=False):
                        retrieved_rows = gradio.Dataframe(
                            interactive=False,
                            height=325,
                            visible=False,
                        )
                        retrieved_rows_label = gradio.Label(
                            value="No rows retrieved",
                            visible=True,
                            show_label=False,
                        )

            with gradio.Tab("Help"):
                gradio.Markdown(
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
            query_button.click(
                fn=self._ask_collection,
                inputs=[
                    query,
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
