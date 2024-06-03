import sys
from typing import Optional, Tuple, Dict

import gradio
import pandas as pd

from dbally import BaseStructuredView
from dbally.collection import Collection
from dbally.similarity import SimilarityIndex
from dbally.utils.errors import UnsupportedQueryError
from dbally.utils.gradio_log_redirect import Logger


sys.stdout = Logger("console.log")


class GradioAdapter:
    """A class to adapt Gradio interface with a similarity store and data operations."""

    SQL_RESULT = "sql"
    PANDAS_RESULT = "filter_mask"

    def __init__(self, similarity_store: SimilarityIndex = None, engine=None):
        """Initializes the GradioAdapter with an optional similarity store.

        Args:
            similarity_store: An instance of SimilarityIndex for similarity operations. Defaults to None.
        """
        self.collection = None
        self.similarity_store = similarity_store
        self.loaded_dataframe = None
        sys.stdout.flush()

    async def ui_load_preview_data(self, selected_view_name: str) -> Tuple[pd.DataFrame, str, None, None, None, None]:
        """Loads selected view data into the adapter.

        Args:
            selected_view_name: The name of the view to load.

        Returns:
            A tuple containing the loaded DataFrame and a message indicating the view data has been loaded.
        """
        preview_dataframe, load_status_text = self.load_preview_data(selected_view_name)
        return preview_dataframe, load_status_text, None, None, None, None

    def load_preview_data(self, selected_view_name: str):
        selected_view = self.collection.get(selected_view_name)
        text_to_display = "No data preview available"
        if issubclass(type(selected_view), BaseStructuredView):
            selected_view_results = selected_view.execute()
            preview_dataframe = pd.DataFrame.from_records(selected_view_results.results)
            text_to_display = "Data preview loaded"
        else:
            preview_dataframe = pd.DataFrame()

        return preview_dataframe, text_to_display

    async def ui_ask_query(self, question_query: str) -> Tuple[Dict, Optional[pd.DataFrame], str]:
        """Executes a query against the collection.

        Args:
            question_query: The question to ask.

        Returns:
            A tuple containing the generated SQL (str) and the resulting DataFrame (pd.DataFrame).
            If the query is unsupported, returns a message indicating this and None.
        """
        try:
            if self.similarity_store:
                await self.similarity_store.update()

            execution_result = await self.collection.ask(question=question_query)
            if self.SQL_RESULT in execution_result.context:
                generated_query = execution_result.context.get(self.SQL_RESULT)
            elif self.PANDAS_RESULT in execution_result.context:
                generated_query = execution_result.context.get(self.PANDAS_RESULT)
            else:
                generated_query = "Unsupported generated query"

            data = pd.DataFrame.from_records(execution_result.results)
        except UnsupportedQueryError:
            generated_query = {"Query": "unsupported"}
            data = pd.DataFrame()
        finally:
            sys.stdout.flush()
            with open("output.log", "r") as f:
                log = f.read()

        return generated_query, data, log

    async def create_interface(self, user_collection: Collection) -> Optional[gradio.Interface]:
        """Creates a Gradio interface for the provided user collection.

        Args:
            user_collection: The user collection to create an interface for.

        Returns:
            The created Gradio interface, or None if no views are available in the collection.
        """
        self.collection = user_collection
        view_list = [*user_collection.list()]
        print(view_list[0])
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
                    loaded_data_frame = gradio.Dataframe(data_preview_frame)

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
