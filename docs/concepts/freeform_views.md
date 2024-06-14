# Concept: Freeform Views

Freeform views are a type of [view](views.md) that provides a way for developers using db-ally to define what they need from the LLM without requiring a fixed response structure. This flexibility is beneficial when the data structure is unknown beforehand or when potential queries are too diverse to be covered by a structured view. Though freeform views offer more flexibility than structured views, they are less predictable, efficient, and secure, and may be more challenging to integrate with other systems. For these reasons, we recommend using [structured views](./structured_views.md) when possible.

Unlike structured views, which define a response format and a set of operations the LLM may use in response to natural language queries, freeform views only have one task - to respond directly to natural language queries with data from the datasource. They accomplish this by implementing the [`ask`][dbally.views.base.BaseView.ask] method. This method takes a natural language query as input and returns a response. The method also has access to the LLM model (via the `llm` attribute), which is typically used to retrieve the correct data from the source (for example, by generating a source-specific query string).

!!! example
    For instance, this is a simple view that uses SQLAlchemy to query candidate table in a SQL database. It contains a single table definition, which LLM will use to generate the appropriate SQL query to answer the question:

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

To learn more about implementing freeform views, refer to the [How to: Create text-to-SQL Freeform View](../how-to/views/text-to-sql.md) guide.

!!! warning
    When using freeform views, the LLM typically gets raw access to the data source and can execute arbitrary operations on it using the query language of the data source (e.g., SQL). This can be powerful but also necessitates that the developer be extremely cautious about securing the data source outside of db-ally. For instance, in the case of Relational Databases, the developer should ensure that the database user used by db-ally has read-only access to the database, and that the database does not contain any sensitive data that shouldn't be exposed to the LLM.
