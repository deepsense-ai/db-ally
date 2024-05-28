from typing import Optional, Tuple

import gradio
import pandas as pd

from dbally.collection import Collection
from dbally.similarity import SimilarityIndex
from dbally.utils.errors import UnsupportedQueryError


class GradioAdapter:
    """A class to adapt Gradio interface with a similarity store and data operations."""

    def __init__(self, similarity_store: SimilarityIndex = None):
        """Initializes the GradioAdapter with an optional similarity store.

        Args:
            similarity_store: An instance of SimilarityIndex for similarity operations. Defaults to None.
        """
        self.collection = None
        self.similarity_store = similarity_store
        self.loaded_dataframe = None

    async def load_data(self, input_dataframe: pd.DataFrame) -> str:
        """Loads data into the adapter from a given DataFrame.

        Args:
            input_dataframe: The DataFrame to load.

        Returns:
            A message indicating the data has been loaded.
        """
        if self.similarity_store:
            await self.similarity_store.update()
        self.loaded_dataframe = input_dataframe
        return "Frame data loaded."

    async def load_selected_data(self, selected_view: str) -> Tuple[pd.DataFrame, str]:
        """Loads selected view data into the adapter.

        Args:
            selected_view: The name of the view to load.

        Returns:
            A tuple containing the loaded DataFrame and a message indicating the view data has been loaded.
        """
        if self.similarity_store:
            await self.similarity_store.update()
            self.loaded_dataframe = pd.DataFrame.from_records(self.collection.get(selected_view).execute().results)
        return self.loaded_dataframe, f"{selected_view} data loaded."

    async def execute_query(self, query: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Executes a query against the collection.

        Args:
            query: The question to ask.

        Returns:
            A tuple containing the generated SQL (str) and the resulting DataFrame (pd.DataFrame).
            If the query is unsupported, returns a message indicating this and None.
        """
        try:
            execution_result = await self.collection.ask(query)
            result = execution_result.context.get("sql"), pd.DataFrame.from_records(execution_result.results)
        except UnsupportedQueryError:
            result = "Unsupported query", None
        return result

    def create_interface(self, user_collection: Collection) -> Optional[gradio.Interface]:
        """Creates a Gradio interface for the provided user collection.

        Args:
            user_collection: The user collection to create an interface for.

        Returns:
            The created Gradio interface, or None if no views are available in the collection.
        """
        view_list = user_collection.list()
        if not view_list:
            print("There is no data to be loaded")
            return None

        self.collection = user_collection

        with gradio.Blocks() as demo:
            with gradio.Row():
                with gradio.Column():
                    view_dropdown = gradio.Dropdown(label="Available views", choices=view_list)
                    load_info = gradio.Label(value="No data loaded.")
                with gradio.Column():
                    loaded_data_frame = gradio.Dataframe(interactive=True, col_count=(4, "Fixed"))
                    load_data_button = gradio.Button("Load new data")
            with gradio.Row():
                query = gradio.Text(label="Ask question")
                query_button = gradio.Button("Proceed")
            with gradio.Row():
                query_sql_result = gradio.Text(label="Generated SQL")
                query_result_frame = gradio.Dataframe(interactive=False)

            view_dropdown.change(
                fn=self.load_selected_data, inputs=view_dropdown, outputs=[loaded_data_frame, load_info]
            )
            load_data_button.click(fn=self.load_data, inputs=loaded_data_frame, outputs=load_info)
            query_button.click(fn=self.execute_query, inputs=[query], outputs=[query_sql_result, query_result_frame])

        return demo
