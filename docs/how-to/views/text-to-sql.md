# How-To: Create text-to-SQL Freeform View

In this guide, you will learn how to write a freeform view that uses a SQL database as a data source. You will understand the internals of text-to-SQL views and learn how to use the codegen feature provided by db-ally to streamline view creation.

## Manual setup

Initially, you may want to create your own freeform view manually. To do so, use the [`BaseText2SQLView`](../../reference/views/text-to-sql.md#dbally.views.freeform.text2sql.view.BaseText2SQLView) class provided by db-ally. To define your view, create a class inheriting from [`BaseText2SQLView`](../../reference/views/text-to-sql.md#dbally.views.freeform.text2sql.view.BaseText2SQLView) and implement the [`get_tables`](../../reference/views/text-to-sql.md#dbally.views.freeform.text2sql.view.BaseText2SQLView.get_tables) method, which returns a list of [`TableConfig`](../../reference/views/text-to-sql.md#dbally.views.freeform.text2sql.config.TableConfig) objects:

```python
class CandidateView(BaseText2SQLView):
    """
    A view for retrieving candidates from the database.
    """

    def get_tables(self) -> List[TableConfig]:
        """
        Defines the tables available in the database.
        """
        return [
            TableConfig(
                name="candidate",
                columns=[
                    ColumnConfig(
                        name="name",
                        data_type="VARCHAR",
                    ),
                    ColumnConfig(
                        name="country",
                        data_type="VARCHAR",
                    ),
                    ...
                ],
            ),
            ...
        ]
```

The returned list contains [`TableConfig`](../../reference/views/text-to-sql.md#dbally.views.freeform.text2sql.config.TableConfig) objects for each table in the database that the LLM should know about, answering the question. At this point you can decide what kind of data the LLM model should have access to, whether at the table or column level, you can limit the visibility of the data at this point.

!!! note
    As you may notice there is no need to define IQL specific features like filters, filtering and building query will be handled be the LLM in this case.

## Autodiscovery

db-ally allows you to automatically retrieve table configurations from any SQL database. You can also use `LLM` to fill in missing table descriptions, and suggest the use of a similarity index for a given column. To start the autodiscovery process, create an `AutodiscoveryBuilder` instance with the `configure_text2sql_auto_discovery` factory method, and then run the `discover` method to start the process.

```python
from dbally.llms.litellm import LiteLLM
from dbally.similarity.index import SimilarityIndex
from dbally_codegen.autodiscovery import configure_text2sql_auto_discovery
from sqlalchemy import create_engine

db = create_engine("sqlite://")
llm = LiteLLM("gpt-3.5-turbo")

builder = (
    configure_text2sql_auto_discovery(db)
        .use_llm(llm)
        .generate_description_by_llm()
        .suggest_similarity_indexes(lambda eng, tab, col: SimilarityIndex(...))
)
tables = await builder.discover()
```

The `tables` variable contains all the table configurations of a given data source and can be used to define a freeform view.

## Code generation

Manual configuration does not scale well for large databases, as writing any view for such cases is tedious and error-prone. Db-ally comes with a codegen feature that uses an autodiscovery mechanism to generate a ready-to-use views for any data source. In order to generate text-to-SQL freeform view run the following command:

```bash
dbally generate-txt2sql-view
```

When you run this command, you will be asked to enter the configuration settings for the autodiscovery process, which include selecting:

- The path to the file where the view will be generated
- The database connection string
- The path to the LLM object.
- The path to the similarity index factory.

Below is a sample autodiscovery configuration:

```bash
File path [text2sql_view.py]: views/text2sql.py
Database URL [sqlite://]: postgresql://user:password@localhost:5432/app
LLM object [None]: litellm:gpt-4o
LLM table description? [y/N]: y
Similarity index factory [None]: faiss
```

After specifying the parameters, the command will start the autodiscovery process and generate the code for the freeform view. Having the file, you can import it and connect it to your collection.

## Using the view

Having implemented the view, you can now use it in your collection and ask it questions.

```python
import dbally
from dbally.llms.litellm import LiteLLM
from sqlalchemy import create_engine

db = create_engine("sqlite://")
llm = LiteLLM("gpt-3.5-turbo")

collection = dbally.create_collection("text-to-sql", llm=llm)
collection.add(CandidateView, lambda: CandidateView(db))

response = await collection.ask("Find me French candidates suitable for a senior data scientist position.")
```
