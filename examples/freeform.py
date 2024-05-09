import asyncio

import sqlalchemy

import dbally
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llm_client.openai_client import OpenAIClient
from dbally.views.freeform.text2sql import Text2SQLConfig, Text2SQLFreeformView, Text2SQLTableConfig


async def main():
    """Main function to run the example."""
    config = Text2SQLConfig(
        tables={
            "customers": Text2SQLTableConfig(
                ddl="CREATE TABLE customers (id INTEGER, name TEXT, city TEXT, country TEXT, age INTEGER)",
                description="Table of customers",
                similarity={"city": "city", "country": "country"},
            ),
            "products": Text2SQLTableConfig(
                ddl="CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL)",
                description="Table of products",
                similarity={"name": "name", "category": "category"},
            ),
            "purchases": Text2SQLTableConfig(
                ddl="CREATE TABLE purchases (customer_id INTEGER, product_id INTEGER, quantity INTEGER, date TEXT)",
                description="Table of purchases",
                similarity={},
            ),
        }
    )
    engine = sqlalchemy.create_engine("sqlite:///:memory:")

    # Create tables from config
    with engine.connect() as connection:
        for _, table_config in config.tables.items():
            connection.execute(sqlalchemy.text(table_config.ddl))

    llm_client = OpenAIClient()
    collection = dbally.create_collection("text2sql", llm_client=llm_client, event_handlers=[CLIEventHandler()])
    collection.add(Text2SQLFreeformView, lambda: Text2SQLFreeformView(engine, config))

    await collection.ask("What are the names of products bought by customers from London?")
    await collection.ask("Which customers bought products from the category 'electronics'?")
    await collection.ask("What is the total quantity of products bought by customers from the UK?")


if __name__ == "__main__":
    asyncio.run(main())
