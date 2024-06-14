# Concept: Structured Views

Structured views are a type of [view](../concepts/views.md), which provide a way for developers using db-ally to define what they need from the LLM, including:

* The desired data structure, such as the specific fields to include from the data source.
* A set of operations the LLM may employ in response to natural language queries (currently only “filters” are supported, with more to come)

Given different natural language queries, a db-ally view will produce different responses while maintaining a consistent data structure. This consistency offers a reliable interface for integration - the code consuming responses from a particular structured view knows what data structure to expect and can utilize this knowledge when displaying or processing the data. This feature of db-ally makes it stand out in terms of reliability and stability compared to standard text-to-SQL approaches.

Each structured view can contain one or more “filters”, which the LLM may decide to choose and apply to the extracted data so that it meets the criteria specified in the natural language query. Given such a query, LLM chooses which filters to use, provides arguments to the filters, and connects the filters with Boolean operators. The LLM expresses these filter combinations using a special language called [IQL](iql.md), in which the defined view filters provide a layer of abstraction between the LLM and the raw syntax used to query the data source (e.g., SQL).

!!! example
    For instance, this is a simple [view that uses SQLAlchemy](../how-to/views/sql.md) to select data from specific columns in a SQL database. It contains a single filter, that the LLM may optionally use to control which table rows to fetch:

    ```python
    class CandidateView(SqlAlchemyBaseView):
        """
        A view for retrieving candidates from the database.
        """

        def get_select(self):
            """
            Defines which columns to select
            """
            return sqlalchemy.select(Candidate.id, Candidate.name, Candidate.country)

        @decorators.view_filter()
        def from_country(self, country: str):
            """
            Filter candidates from a specific country.
            """
            return Candidate.country == country
    ```

In addition to structured views, db-ally also provides [freeform views](freeform_views.md), which are more flexible and can be used to create views that do not require a fixed data structure. Freeform views come in handy when the data structure is not predefined or when the scope of potential queries is too vast to be addressed by a structured view. Conversely, structured views are more predictable, efficient, secure, and easier to integrate with other systems. Therefore, we recommend using structured views where possible. To read about the advantages and disadvantages of both kinds of views, refer to [Concept: Views](views.md).

A project can implement several structured views, each tailored to different output formats and filters to suit various use cases. It can also combine structured views with freeform views to allow a more flexible interface for users. The LLM selects the most suitable view that best matches the specific natural language query. For more information, you consider reading our article on [Collections](collections.md).

See the [Quickstart](../quickstart/index.md) guide for a complete example of how to define and use structured views.