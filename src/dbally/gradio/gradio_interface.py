import json
from io import StringIO
from typing import Any, Dict, List, Tuple

import gradio
import pandas as pd

from dbally import BaseStructuredView
from dbally.audit import CLIEventHandler
from dbally.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.prompt.template import PromptTemplateError


async def create_gradio_interface(user_collection: Collection, preview_limit: int = 10) -> gradio.Interface:
    """Adapt and integrate data collection and query execution with Gradio interface components.

    Args:
        user_collection: The user's collection to interact with.
        preview_limit: The maximum number of preview data records to display. Default is 10.

    Returns:
        The created Gradio interface.
    """
    adapter = GradioAdapter()
    gradio_interface = await adapter.create_interface(user_collection, preview_limit)
    return gradio_interface


class GradioAdapter:
    """
    A class to adapt and integrate data collection and query execution with Gradio interface components.
    """

    def __init__(self):
        """
        Initializes the GradioAdapter with a preview limit.

        """
        self.preview_limit = None
        self.selected_view_name = None
        self.collection = None
        self.log = StringIO()

    def _load_gradio_data(self, preview_dataframe, label, empty_warning=None) -> Tuple[gradio.DataFrame, gradio.Label]:
        if not empty_warning:
            empty_warning = "Preview not available"

        if preview_dataframe.empty:
            gradio_preview_dataframe = gradio.DataFrame(label=label, value=preview_dataframe, visible=False)
            empty_frame_label = gradio.Label(value=f"{label} not available", visible=True, show_label=False)
        else:
            gradio_preview_dataframe = gradio.DataFrame(label=label, value=preview_dataframe, visible=True)
            empty_frame_label = gradio.Label(value=f"{label} not available", visible=False, show_label=False)
        return gradio_preview_dataframe, empty_frame_label

    async def _ui_load_preview_data(
        self, selected_view_name: str
    ) -> Tuple[gradio.DataFrame, gradio.Label, None, None, None]:
        """
        Asynchronously loads preview data for a selected view name.

        Args:
            selected_view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe, load status text, and four None values to clean gradio fields.
        """
        self.selected_view_name = selected_view_name
        preview_dataframe = self._load_preview_data(selected_view_name)
        gradio_preview_dataframe, empty_frame_label = self._load_gradio_data(preview_dataframe, "Preview")

        return gradio_preview_dataframe, empty_frame_label, None, None, None

    def _load_preview_data(self, selected_view_name: str) -> pd.DataFrame:
        """
        Loads preview data for a selected view name.

        Args:
            selected_view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe
        """
        selected_view = self.collection.get(selected_view_name)
        if issubclass(type(selected_view), BaseStructuredView):
            selected_view_results = selected_view.execute()
            preview_dataframe = self._load_results_into_dataframe(selected_view_results.results).head(
                self.preview_limit
            )
        else:
            preview_dataframe = pd.DataFrame()

        return preview_dataframe

    async def _ui_ask_query(
        self, question_query: str, natural_language_flag: bool
    ) -> Tuple[gradio.DataFrame, gradio.Label, gradio.Text, gradio.Text, str]:
        """
        Asynchronously processes a query and returns the results.

        Args:
            question_query: The query to process.
            natural_language_flag: Flag to indicate if the natural language shall be returned

        Returns:
            A tuple containing the generated query context, the query results as a dataframe, and the log output.
        """
        self.log.seek(0)
        self.log.truncate(0)
        textual_response = ""
        try:
            execution_result = await self.collection.ask(
                question=question_query, return_natural_response=natural_language_flag
            )
            generated_query = str(execution_result.context)
            data = self._load_results_into_dataframe(execution_result.results)
            textual_response = str(execution_result.textual_response) if natural_language_flag else textual_response
        except UnsupportedQueryError:
            generated_query = {"Query": "unsupported"}
            data = pd.DataFrame()
        except NoViewFoundError:
            generated_query = {"Query": "No view matched to query"}
            data = pd.DataFrame()
        except PromptTemplateError:
            generated_query = {"Query": "No view matched to query"}
            data = pd.DataFrame()
        finally:
            self.log.seek(0)
            log_content = self.log.read()

        gradio_dataframe, empty_dataframe_warning = self._load_gradio_data(data, "Results", "No matching results found")
        return (
            gradio_dataframe,
            empty_dataframe_warning,
            gradio.Text(value=generated_query, visible=True),
            gradio.Text(value=textual_response, visible=natural_language_flag),
            log_content,
        )

    def _clear_results(self) -> Tuple[gradio.DataFrame, gradio.Label, gradio.Text, gradio.Text]:
        preview_dataframe = self._load_preview_data(self.selected_view_name)
        gradio_preview_dataframe, empty_frame_label = self._load_gradio_data(preview_dataframe, "Preview")

        return (
            gradio_preview_dataframe,
            empty_frame_label,
            gradio.Text(visible=False),
            gradio.Text(visible=False),
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

    async def create_interface(self, user_collection: Collection, preview_limit: int) -> gradio.Interface:
        """
        Creates a Gradio interface for interacting with the user collection and similarity stores.

        Args:
            user_collection: The user's collection to interact with.
            preview_limit: The maximum number of preview data records to display.

        Returns:
            The created Gradio interface.
        """

        self.preview_limit = preview_limit
        self.collection = user_collection
        self.collection.add_event_handler(CLIEventHandler(self.log))

        data_preview_frame = pd.DataFrame()
        question_interactive = False

        view_list = [*user_collection.list()]
        if view_list:
            self.selected_view_name = view_list[0]
            data_preview_frame = self._load_preview_data(self.selected_view_name)
            question_interactive = True

        with gradio.Blocks() as demo:
            with gradio.Row():
                with gradio.Column():
                    view_dropdown = gradio.Dropdown(
                        label="Data View preview", choices=view_list, value=self.selected_view_name
                    )
                    query = gradio.Text(label="Ask question", interactive=question_interactive)
                    query_button = gradio.Button("Ask db-ally", interactive=question_interactive)
                    clear_button = gradio.ClearButton(components=[query], interactive=question_interactive)
                    natural_language_response_checkbox = gradio.Checkbox(
                        label="Return natural language answer", interactive=question_interactive
                    )

                with gradio.Column():
                    if not data_preview_frame.empty:
                        loaded_data_frame = gradio.Dataframe(
                            label="Preview", value=data_preview_frame, interactive=False
                        )
                        empty_frame_label = gradio.Label(value="Preview not available", visible=False)
                    else:
                        loaded_data_frame = gradio.Dataframe(interactive=False, visible=False)
                        empty_frame_label = gradio.Label(value="Preview not available", visible=True)

                    query_sql_result = gradio.Text(label="Generated query context", visible=False)
                    generated_natural_language_answer = gradio.Text(
                        label="Generated answer in natural language:", visible=False
                    )

            with gradio.Row():
                log_console = gradio.Code(label="Logs", language="shell")

            clear_button.add(
                [
                    natural_language_response_checkbox,
                    loaded_data_frame,
                    query_sql_result,
                    generated_natural_language_answer,
                    log_console,
                ]
            )

            clear_button.click(
                fn=self._clear_results,
                inputs=[],
                outputs=[
                    loaded_data_frame,
                    empty_frame_label,
                    query_sql_result,
                    generated_natural_language_answer,
                ],
            )

            view_dropdown.change(
                fn=self._ui_load_preview_data,
                inputs=view_dropdown,
                outputs=[
                    loaded_data_frame,
                    empty_frame_label,
                    query,
                    query_sql_result,
                    log_console,
                ],
            )
            query_button.click(
                fn=self._ui_ask_query,
                inputs=[query, natural_language_response_checkbox],
                outputs=[
                    loaded_data_frame,
                    empty_frame_label,
                    query_sql_result,
                    generated_natural_language_answer,
                    log_console,
                ],
            )

        return demo
