import sys
from typing import Dict, List, Optional, Tuple

import gradio
import pandas as pd

from dbally import BaseStructuredView
from dbally.collection import Collection
from dbally.prompts import PromptTemplateError
from dbally.similarity import SimilarityIndex
from dbally.utils.errors import NoViewFoundError, UnsupportedQueryError
from dbally.utils.log_to_file import FileLogger

CONSOLE_FILE_NAME = "console.log"
sys.stdout = FileLogger(CONSOLE_FILE_NAME)


class GradioAdapter:
    """
    A class to adapt and integrate data collection and query execution with Gradio interface components.
    """

    def __init__(self, preview_limit: int = 20):
        """
        Initializes the GradioAdapter with a preview limit.

        Args:
            preview_limit: The maximum number of preview data records to display. Default is 20.
        """
        self.preview_limit = preview_limit
        self.similarity_store_list = []
        self.collection = None
        sys.stdout.flush()

    async def ui_load_preview_data(self, selected_view_name: str) -> Tuple[pd.DataFrame, str, None, None, None, None]:
        """
        Asynchronously loads preview data for a selected view name.

        Args:
            selected_view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe, load status text, and four None values to clean gradio fields.
        """
        preview_dataframe, load_status_text = self.load_preview_data(selected_view_name)
        return preview_dataframe, load_status_text, None, None, None, None

    def load_preview_data(self, selected_view_name: str) -> Tuple[pd.DataFrame, str]:
        """
        Loads preview data for a selected view name.

        Args:
            selected_view_name: The name of the selected view to load preview data for.

        Returns:
            A tuple containing the preview dataframe and load status text.
        """
        selected_view = self.collection.get(selected_view_name)
        text_to_display = "No data preview available"
        if issubclass(type(selected_view), BaseStructuredView):
            selected_view_results = selected_view.execute()
            preview_dataframe = pd.DataFrame.from_records(selected_view_results.results).head(self.preview_limit)
            text_to_display = "Data preview loaded"
        else:
            preview_dataframe = pd.DataFrame()

        return preview_dataframe, text_to_display

    async def ui_ask_query(self, question_query: str) -> Tuple[Dict, Optional[pd.DataFrame], str]:
        """
        Asynchronously processes a query and returns the results.

        Args:
            question_query (str): The query to process.

        Returns:
            A tuple containing the generated query context, the query results as a dataframe, and the log output.
        """
        try:
            for similarity_store in self.similarity_store_list:
                await similarity_store.update()

            execution_result = await self.collection.ask(question=question_query)
            generated_query = str(execution_result.context)
            data = pd.DataFrame.from_records(execution_result.results)
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
            sys.stdout.flush()
            with open(CONSOLE_FILE_NAME, encoding="utf8") as console_log_file:
                log = console_log_file.read()

        return generated_query, data, log

    async def create_interface(
        self, user_collection: Collection, similarity_store_list: Optional[List[SimilarityIndex]] = None
    ) -> Optional[gradio.Interface]:
        """
        Creates a Gradio interface for interacting with the user collection and similarity stores.

        Args:
            user_collection: The user's collection to interact with.
            similarity_store_list: A list of similarity stores. Default is None.

        Returns:
            The created Gradio interface, or None if no data is available to load.

        Raises:
             ValueError: occurs when there is no view define in collection.
        """
        self.collection = user_collection
        if not similarity_store_list:
            self.similarity_store_list = similarity_store_list

        view_list = [*user_collection.list()]
        if view_list:
            default_selected_view_name = view_list[0]
        else:
            raise ValueError("No view to display")

        if not view_list:
            print("There is no data to be loaded")
            return None

        with gradio.Blocks() as demo:
            with gradio.Row():
                with gradio.Column():
                    view_dropdown = gradio.Dropdown(
                        label="Data View preview", choices=view_list, value=default_selected_view_name
                    )
                with gradio.Column():
                    data_preview_frame, data_preview_status = self.load_preview_data(view_list[0])

                    data_preview_info = gradio.Text(label="Data preview", value=data_preview_status)
                    if not data_preview_frame.empty:
                        loaded_data_frame = gradio.Dataframe(value=data_preview_frame, interactive=False)
                    else:
                        loaded_data_frame = gradio.Dataframe(interactive=False)

            with gradio.Row():
                query = gradio.Text(label="Ask question")
                query_button = gradio.Button("Proceed")
            with gradio.Row():
                query_sql_result = gradio.Text(label="Generated query context")
                query_result_frame = gradio.Dataframe(interactive=False)
            with gradio.Row():
                log_console = gradio.Code(label="Logs")

            view_dropdown.change(
                fn=self.ui_load_preview_data,
                inputs=view_dropdown,
                outputs=[
                    loaded_data_frame,
                    data_preview_info,
                    query,
                    query_sql_result,
                    query_result_frame,
                    log_console,
                ],
            )
            query_button.click(
                fn=self.ui_ask_query, inputs=[query], outputs=[query_sql_result, query_result_frame, log_console]
            )

        return demo
