import os

print("Installing dependencies...")
os.system("pip install -U langgraph langchain langchain_openai langchain_experimental dbally[openai,langsmith]")
print("Dependencies installed")

from urllib import request
from sqlalchemy import create_engine, text

import asyncio

from dbally import Collection

import dbally
from dbally.views.freeform.text2sql import configure_text2sql_auto_discovery, Text2SQLFreeformView

from langchain_openai import ChatOpenAI

from langgraph.graph import END, StateGraph

from typing import Optional
from dbally.llm_client.openai_client import OpenAIClient
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.manager import CallbackManagerForToolRun
from dbally.utils.errors import UnsupportedQueryError

from langgraph.graph.message import add_messages, AnyMessage
from typing_extensions import TypedDict
from typing import Annotated, Type
from langchain_core.runnables import Runnable

from langgraph.checkpoint.sqlite import SqliteSaver

from uuid import uuid4

unique_id = uuid4().hex[0:8]

# UNCOMMENT THIS TO USE LANGSMITH!
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = ""
# os.environ["LANGCHAIN_PROJECT"] = f"langgraph-dbally - {unique_id}"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

################################################################################
#Dbally Tool definition
################################################################################


class DatabaseQuery(BaseModel):
    query: str = Field(description="should be a query to the database in the natural language.")


class DballyTool(BaseTool):
    name = "dbally"
    description: str
    collection: Collection
    args_schema: Type[BaseModel] = DatabaseQuery

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        try:
            result = asyncio.run(self.collection.ask(query))

            if result.textual_response is not None:
                return result.textual_response
            else:
                return result.results
        except UnsupportedQueryError:
            return "database master can't answer this question"

###################################################################################
# Database definition
##################################################################################

def set_database():
    print("Downloading the HR database")
    request.urlretrieve('https://drive.google.com/uc?export=download&id=1zo3j8x7qH8opTKyQ9qFgRpS3yqU6uTRs', 'recruitment.db')
    print("Database downloaded")
    print("Creating the database")

    db_engine = create_engine("sqlite:///recruitment.db")

    print("Displaying the first 5 rows of the candidate table")

    with db_engine.connect() as conn:
        rows = conn.execute(text("SELECT * from candidate LIMIT 5")).fetchall()

    print(rows)

    return db_engine

###################################################################################
#Definition of:
# 1. State of the Graph
# 2. Assistant Node
# 3. Assistant's prompt
###################################################################################


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State):
        result = self.runnable.invoke(state)
        return {"messages": result}


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful talent aquisition assistant "
            " Use the provided tools to search for candidates, job offers, and other information to assist the user's queries. "
        ),
        ("placeholder", "{messages}"),
    ]
)
###################################################################################
# Creating nodes of the graph and connecting them
###################################################################################


def build_graph(recruitment_db: Collection):
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    tools = [DballyTool(collection=recruitment_db, description="useful for when you need to gather some HR data")]
    runnable = primary_assistant_prompt | llm.bind_tools(tools)

    tool_node = ToolNode(tools)
    assistant_node = Assistant(runnable)

    graph = StateGraph(State)
    graph.add_node("assistant", assistant_node)
    graph.add_node("action", tool_node)
    graph.set_entry_point("assistant")

    graph.add_edge("action", "assistant")
    graph.add_conditional_edges(
        "assistant",
        tools_condition,
        # "action" calls one of our tools. END causes the graph to terminate (and respond to the user)
        {"action": "action", END: END},
    )

    memory = SqliteSaver.from_conn_string(":memory:")
    app = graph.compile(checkpointer=memory)

    return app

def main():
    db_engine = set_database()
    os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API Key: ")

    # Configure the text2sql view
    view_config = asyncio.run(configure_text2sql_auto_discovery(db_engine).discover())
    recruitment_db = dbally.create_collection("recruitment", llm_client=OpenAIClient())
    recruitment_db.add(Text2SQLFreeformView, lambda: Text2SQLFreeformView(db_engine, view_config))

    #Build the graph
    app = build_graph(recruitment_db=recruitment_db)

    #Set thread id to remember entire conversation
    graph_config = {
        "configurable": {
            "thread_id": unique_id,
        }
    }

    while True:
        question = input("Enter your message: ")
        events = app.stream(
            {"messages": ("user", question)}, graph_config, stream_mode="values"
        )
        for event in events:
            event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()