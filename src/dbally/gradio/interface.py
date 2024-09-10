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
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping


def create_gradio_interface(
    collection: Collection,
    *,
    title: str = "db-ally lab",
    header: str = "🔍 db-ally lab",
    examples: Optional[List[str]] = None,
    examples_per_page: int = 4,
    preview_limit: Optional[int] = None,
) -> gr.Interface:
    """
    Creates a Gradio interface for interacting with the user collection and similarity stores.

    Args:
        collection: The collection to interact with.
        title: The title of the gradio interface.
        header: The header of the gradio interface.
        examples: The example questions to display.
        examples_per_page: The number of examples to display per page.
        preview_limit: The maximum number of preview data records to display. Default is None.

    Returns:
        The created Gradio interface.
    """
    adapter = GradioAdapter(
        collection=collection,
        title=title,
        header=header,
        examples=examples,
        examples_per_page=examples_per_page,
        preview_limit=preview_limit,
    )
    return adapter.create_interface()


class GradioAdapter:
    """
    Gradio adapter for the db-ally lab.
    """

    def __init__(
        self,
        collection: Collection,
        *,
        title: str = "db-ally lab",
        header: str = "🔍 db-ally lab",
        examples: Optional[List[str]] = None,
        examples_per_page: int = 4,
        preview_limit: Optional[int] = None,
    ) -> None:
        """
        Creates the gradio adapter.

        Args:
            collection: The collection to interact with.
            title: The title of the gradio interface.
            header: The header of the gradio interface.
            examples: The example questions to display.
            examples_per_page: The number of examples to display per page.
            preview_limit: The maximum number of preview data records to display.
        """
        self.collection = collection
        self.preview_limit = preview_limit
        self.title = title
        self.header = header
        self.examples = examples or []
        self.examples_per_page = examples_per_page
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
        except (NoViewFoundError, ViewExecutionError) as e:
            view_name = e.view_name
            sql = ""
            iql_filters = ""
            iql_aggregation = ""
            retrieved_rows = pd.DataFrame()
            textual_response = ""
        else:
            view_name = result.view_name
            sql = result.context.get("sql", "")
            iql_filters = result.context.get("iql", {}).get("filters", "")
            iql_aggregation = result.context.get("iql", {}).get("aggregation", "")
            retrieved_rows = self._load_results_into_dataframe(result.results)
            textual_response = result.textual_response or ""

        retrieved_rows, empty_retrieved_rows_warning = self._render_dataframe(retrieved_rows, "No rows retrieved")

        self.log.seek(0)
        log_content = self.log.read()

        return (
            gr.Textbox(value=textual_response, visible=return_natural_response),
            gr.Textbox(value=view_name, visible=True),
            gr.Code(value=iql_filters, visible=bool(iql_filters)),
            gr.Code(value=iql_aggregation, visible=bool(iql_aggregation)),
            gr.Code(value=sql, visible=bool(sql)),
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

    def _render_param(self, param: MethodParamWithTyping) -> str:
        if param.similarity_index:
            return f"{param.name}: {str(param.type).replace('typing.', '')}"
        return str(param)

    def _render_tab_data(self, data: pd.DataFrame) -> None:
        with gr.Tab("Data"):
            if data.empty:
                gr.Label("No data available", show_label=False)
            else:
                gr.Dataframe(value=data, height=320)

    def _render_tab_iql(self, methods: List[ExposedFunction], label: str) -> None:
        with gr.Tab(f"IQL {label}"):
            if methods:
                gr.Dataframe(
                    value=[
                        [
                            f"{method.name}({', '.join(self._render_param(param) for param in method.parameters)})",
                            method.description,
                        ]
                        for method in methods
                    ],
                    headers=["signature", "description"],
                    interactive=False,
                    height=325,
                )
            else:
                gr.Label(f"No {label.lower()} available", show_label=False)

    def create_interface(self) -> gr.Interface:
        """
        Creates a Gradio interface for interacting with the collection.

        Returns:
            The Gradio interface.
        """
        views = list(self.collection.list())
        selected_view = views[0] if views else None

        with gr.Blocks(title=self.title) as demo:
            gr.Markdown(f"# {self.header}")

            with gr.Tab("Collection"):
                with gr.Row():
                    with gr.Column():
                        api_key = gr.Textbox(
                            label="API Key",
                            placeholder="Enter your API Key",
                            type="password",
                            interactive=bool(selected_view),
                        )
                        model_name = gr.Textbox(
                            label="Model Name",
                            placeholder="Enter your model name",
                            value=self.collection._llm.model_name,  # pylint: disable=protected-access
                            interactive=bool(selected_view),
                            max_lines=1,
                        )
                        question = gr.Textbox(
                            label="Question",
                            placeholder="Enter your question",
                            interactive=bool(selected_view),
                            max_lines=1,
                        )
                        natural_language_response_checkbox = gr.Checkbox(
                            label="Use Natural Language Responder",
                            interactive=bool(selected_view),
                        )

                        if self.examples and selected_view:
                            gr.Examples(
                                label="Example questions",
                                examples=self.examples,
                                inputs=question,
                                examples_per_page=self.examples_per_page,
                            )

                        with gr.Row():
                            clear_button = gr.ClearButton(
                                value="Reset",
                                components=[question],
                                interactive=bool(selected_view),
                            )
                            ask_button = gr.Button(
                                value="Ask",
                                variant="primary",
                                interactive=bool(selected_view),
                            )

                        gr.HTML(
                            """
                            <div style="text-align: end; font-weight: bold;">
                            POWERED BY <a href="https://github.com/deepsense-ai/db-ally" target="_blank">DB-ALLY</a>
                            </div>
                            """
                        )

                    with gr.Column():
                        view_dropdown = gr.Dropdown(
                            label="View Preview",
                            choices=views,
                            value=selected_view,
                            interactive=bool(selected_view),
                        )

                        @gr.render(inputs=view_dropdown, triggers=[demo.load, view_dropdown.change])
                        def render_view_preview(view_name: Optional[str]) -> None:
                            if view_name is None:
                                gr.Label("No views", show_label=False)
                                return

                            view = self.collection.get(view_name)

                            if not isinstance(view, BaseStructuredView):
                                gr.Label(value="Preview not available", show_label=False)
                                return

                            result = view.execute()
                            data = self._load_results_into_dataframe(result.results)
                            if self.preview_limit is not None:
                                data = data.head(self.preview_limit)

                            filters = view.list_filters()
                            aggregations = view.list_aggregations()

                            self._render_tab_data(data)
                            self._render_tab_iql(filters, "Filters")
                            self._render_tab_iql(aggregations, "Aggregations")

                with gr.Tab("Results"):
                    natural_language_response = gr.Textbox(
                        label="Natural Language Response",
                        visible=False,
                    )
                    selected_view_name = gr.Textbox(
                        label="Selected View",
                        visible=False,
                        max_lines=1,
                    )

                    with gr.Row():
                        iql_fitlers_result = gr.Code(
                            label="IQL Filters Query",
                            lines=1,
                            language="python",
                            visible=False,
                        )
                        iql_aggregation_result = gr.Code(
                            label="IQL Aggregation Query",
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
                    log_console = gr.Code(language="shell", show_label=False)

            with gr.Tab("Help"):
                gr.Markdown(
                    """
                    ## How to use this app
                    1. Enter your API Key for the LLM you want to use in the provided field.
                    2. Choose the [model](https://docs.litellm.ai/docs/providers) you want to use.
                    3. Type your question in the textbox.
                    4. Click on `Ask`. The retrieval results will appear in the `Results` tab.

                    ## Learn more
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
                    selected_view_name,
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
                    selected_view_name,
                    iql_fitlers_result,
                    iql_aggregation_result,
                    sql_result,
                    retrieved_rows,
                    retrieved_rows_label,
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
                    natural_language_response,
                    selected_view_name,
                    iql_fitlers_result,
                    iql_aggregation_result,
                    sql_result,
                    retrieved_rows,
                    retrieved_rows_label,
                    log_console,
                ],
            )

        return demo
