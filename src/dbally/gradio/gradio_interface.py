from io import StringIO
from typing import Dict, Optional, Tuple

import gradio
import pandas as pd

from dbally import BaseStructuredView
from dbally.audit import CLIEventHandler
from dbally.collection import Collection
from dbally.prompts import PromptTemplateError
from dbally.utils.errors import NoViewFoundError, UnsupportedQueryError


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
        self.collection = None
        self.log = StringIO()

    async def _ui_load_preview_data(self, selected_view_name: str) -> Tuple[pd.DataFrame, None, None, None, None]:
        """
        Asynchronously loads preview data for a selected view name.

        Args:
            selected_view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe, load status text, and four None values to clean gradio fields.
        """
        preview_dataframe = self._load_preview_data(selected_view_name)
        return preview_dataframe, None, None, None, None

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
            preview_dataframe = pd.DataFrame.from_records(selected_view_results.results).head(self.preview_limit)
        else:
            preview_dataframe = pd.DataFrame()

        return preview_dataframe

    async def _ui_ask_query(
        self, question_query: str, natural_language_flag: bool
    ) -> Tuple[Dict, Optional[pd.DataFrame], str, str]:
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
            data = pd.DataFrame.from_records(execution_result.results)
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
        return generated_query, data, textual_response, log_content

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

        default_selected_view_name = None
        data_preview_frame = pd.DataFrame()
        question_interactive = False

        view_list = [*user_collection.list()]
        if view_list:
            default_selected_view_name = view_list[0]
            data_preview_frame = self._load_preview_data(view_list[0])
            question_interactive = True

        with gradio.Blocks() as demo:
            with gradio.Row():
                with gradio.Column():
                    view_dropdown = gradio.Dropdown(
                        label="Data View preview", choices=view_list, value=default_selected_view_name
                    )
                    query = gradio.Text(label="Ask question", interactive=question_interactive)
                    query_button = gradio.Button("Ask db-ally", interactive=question_interactive)
                    natural_language_response_checkbox = gradio.Checkbox(
                        label="Return natural language answer", interactive=question_interactive
                    )

                with gradio.Column():
                    gradio.Label(show_label=False, value="PREVIEW")
                    if not data_preview_frame.empty:
                        loaded_data_frame = gradio.Dataframe(value=data_preview_frame, interactive=False)
                    else:
                        loaded_data_frame = gradio.Dataframe(interactive=False)
                    gradio.Label(show_label=False, value="RESULT")
                    query_sql_result = gradio.Text(label="Generated query context")
                    generated_natural_language_answer = gradio.Text(label="Generated answer in natural language:")
                    query_result_frame = gradio.Dataframe(interactive=False)

            with gradio.Row():
                log_console = gradio.Code(label="Logs", language="shell")

            view_dropdown.change(
                fn=self._ui_load_preview_data,
                inputs=view_dropdown,
                outputs=[
                    loaded_data_frame,
                    query,
                    query_sql_result,
                    query_result_frame,
                    log_console,
                ],
            )
            query_button.click(
                fn=self._ui_ask_query,
                inputs=[query, natural_language_response_checkbox],
                outputs=[query_sql_result, query_result_frame, generated_natural_language_answer, log_console],
            )

        return demo
