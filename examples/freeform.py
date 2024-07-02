import asyncio
from typing import List

import sqlalchemy

import dbally
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llms import LiteLLM
from dbally.views.freeform.text2sql import BaseText2SQLView, ColumnConfig, TableConfig


class MyText2SqlView(BaseText2SQLView):
    """
    A Text2SQL view for the example.
    """

    def get_tables(self) -> List[TableConfig]:
        """
        Get the tables used by the view.

        Returns:
            A list of tables.
        """
        return [
            TableConfig(
                name="customers",
                columns=[
                    ColumnConfig("id", "SERIAL PRIMARY KEY"),
                    ColumnConfig("name", "VARCHAR(255)"),
                    ColumnConfig("city", "VARCHAR(255)"),
                    ColumnConfig("country", "VARCHAR(255)"),
                    ColumnConfig("age", "INTEGER"),
                ],
            ),
            TableConfig(
                name="products",
                columns=[
                    ColumnConfig("id", "SERIAL PRIMARY KEY"),
                    ColumnConfig("name", "VARCHAR(255)"),
                    ColumnConfig("category", "VARCHAR(255)"),
                    ColumnConfig("price", "REAL"),
                ],
            ),
            TableConfig(
                name="purchases",
                columns=[
                    ColumnConfig("customer_id", "INTEGER"),
                    ColumnConfig("product_id", "INTEGER"),
                    ColumnConfig("quantity", "INTEGER"),
                    ColumnConfig("date", "TEXT"),
                ],
            ),
        ]


async def main():
    """Main function to run the example."""
    engine = sqlalchemy.create_engine("sqlite:///:memory:")

    # Create tables from config
    with engine.connect() as connection:
        for table_config in MyText2SqlView(engine).get_tables():
            connection.execute(sqlalchemy.text(table_config.ddl))

    llm = LiteLLM()
    collection = dbally.create_collection("text2sql", llm=llm, event_handlers=[CLIEventHandler()])
    collection.add(MyText2SqlView, lambda: MyText2SqlView(engine))

    await collection.ask("What are the names of products bought by customers from London?")
    await collection.ask("Which customers bought products from the category 'electronics'?")
    await collection.ask("What is the total quantity of products bought by customers from the UK?")


if __name__ == "__main__":
    asyncio.run(main())
