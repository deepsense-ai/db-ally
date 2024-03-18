
---

<h1 align="center">db-ally</h1>

<p align="center">
    <em>Efficient, consistent and secure library for querying structured data with natural language</em>
</p>

---

**db-ally** is an LLM-powered library for creating natural language interfaces to databases. While it occupies a similar space to the text-to-SQL solutions, its goals and methods are different. db-ally allows developers to outline specific use cases for the LLM to handle, detailing the desired data format and the possible operations to fetch this data.

db-ally effectively shields the complexity of the underlying database from the model, presenting only the essential information needed for solving the specific use cases. Instead of generating arbitrary SQL, the model is asked to generate responses in a simplified query language.

The benefits of db-ally can be described in terms of its four main characteristics:
* **Consistency**: db-ally ensures predictable output formats and confines operations to those predefined by developers, making it particularly well-suited for applications with precise requirements on their behavior or data format
* **Security**: db-ally prevents direct database access and arbitrary SQL execution, bolstering system safety
* **Efficiency**: db-ally hides most of the underlying database complexity, enabling the LLM to concentrate on essential aspects and improving performance
* **Portability**: db-ally introduces an abstraction layer between the model and the database, ensuring easy integration with various database technologies and data sources.

## Quickstart

In db-ally, developers define their use cases by implementing [**views**](docs/concepts/views.md) and **filters**. A list of possible filters is presented to the LLM in terms of [**IQL**](docs/concepts/iql.md) (Intermediate Query Language). Views are grouped and registered within a [**collection**](docs/concepts/views.md), which then serves as an entry point for asking questions in natural language.

Basic implementation of a db-ally view for an example HR application can be found below:

```python
from dbally import decorators
import dbally

class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self):
        """
        Defines which columns to select.
        """
        return sqlalchemy.select(Candidate.id, Candidate.name, Candidate.country)

    @decorators.view_filter()
    def from_country(self, country: str):
        """
        Filter candidates from a specific country.
        """
        return Candidate.country == country


my_collection = dbally.create_collection("my_collection")
my_collection.add(MyView)

my_collection.ask("Find candidates from United States")
```
For a concrete step-by-step example on how to use db-ally, go to [Quickstart](docs/quickstart/quickstart.md) guide. For a more learning-oriented experience, check our db-ally [Tutorial](docs/tutorials/tutorial_1.md).

## Requirements

TBD

## Installation

To install db-ally, execute the following command:

```bash
pip install dbally
```

Additionally, you can install one of our extensions to use specific features.

* `dbally[openai]`: Use [OpenAI's models](https://platform.openai.com/docs/models)
* `dbally[faiss]`: Use [Faiss](https://github.com/facebookresearch/faiss) indexes for similarity search
* `dbally[langsmith]`: Use [LangSmith](https://www.langchain.com/langsmith) for query tracking

```bash
pip install dbally[openai,faiss,langsmith]
```

## License

db-ally is released under MIT license.

## Sponsors

db-ally was originally developed at deepsense.ai

## How db-ally documentation is organized

Do we want this?

## Supported features

- [x] Integration with OpenAI models
- [x] Similarity search
- [x] Integration with LangSmith
- [] Integration with Anyscale Endpoints
- [] Support for analytical queries



