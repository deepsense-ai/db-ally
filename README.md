<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
  <img alt="dbally logo" src="docs/assets/banner-dark.svg" width="40%" height="40%">
</picture>

<br/>
<br/>

<p>
  <em>Efficient, consistent and secure library for querying structured data with natural language</em>
</p>

<h3>

[Homepage](https://deepsense.ai/db-ally) | [Documentation](https://db-ally.deepsense.ai/) | [Contact](mailto:db-ally@deepsense.ai)

</h3>

[![HuggingFace - Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue.svg)](https://huggingface.co/spaces/deepsense-ai/db-ally)
[![PyPI - License](https://img.shields.io/pypi/l/dbally)](https://pypi.org/project/dbally)
[![PyPI - Version](https://img.shields.io/pypi/v/dbally)](https://pypi.org/project/dbally)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dbally)](https://pypi.org/project/dbally)

</div>

---

db-ally is an LLM-powered library for creating natural language interfaces to data sources. While it occupies a similar space to the text-to-SQL solutions, its goals and methods are different. db-ally allows developers to outline specific use cases for the LLM to handle, detailing the desired data format and the possible operations to fetch this data.

db-ally effectively shields the complexity of the underlying data source from the model, presenting only the essential information needed for solving the specific use cases. Instead of generating arbitrary SQL, the model is asked to generate responses in a simplified query language.

The benefits of db-ally can be described in terms of its four main characteristics:

* **Consistency**: db-ally ensures predictable output formats and confines operations to those predefined by developers, making it particularly well-suited for applications with precise requirements on their behavior or data format
* **Security**: db-ally prevents direct database access and arbitrary SQL execution, bolstering system safety
* **Efficiency**: db-ally hides most of the underlying database complexity, enabling the LLM to concentrate on essential aspects and improving performance
* **Portability**: db-ally introduces an abstraction layer between the model and the data, ensuring easy integration with various database technologies and other data sources.

## Quickstart

In db-ally, developers define their use cases by implementing [**views**](https://db-ally.deepsense.ai/concepts/views), **filters** and **aggregations**. A list of possible filters and aggregations is presented to the LLM in terms of [**IQL**](https://db-ally.deepsense.ai/concepts/iql) (Intermediate Query Language). Views are grouped and registered within a [**collection**](https://db-ally.deepsense.ai/concepts/views), which then serves as an entry point for asking questions in natural language.

This is a basic implementation of a db-ally view for an example HR application, which retrieves candidates from an SQL database:

```python
from dbally import decorators, SqlAlchemyBaseView, create_collection
from dbally.llms.litellm import LiteLLM
from sqlalchemy import create_engine

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


llm = LiteLLM(model_name="gpt-3.5-turbo")
engine = create_engine("sqlite:///examples/recruiting/data/candidates.db")

my_collection = create_collection("collection_name", llm)
my_collection.add(CandidateView, lambda: CandidateView(engine))

my_collection.ask("Find candidates from United States")
```

For a concrete step-by-step example on how to use db-ally, go to [Quickstart](https://db-ally.deepsense.ai/quickstart/) guide. For a more learning-oriented experience, check our db-ally [Tutorial](https://db-ally.deepsense.ai/tutorials/).

## Motivation

db-ally was originally developed at [deepsense.ai](https://deepsense.ai). In our work on various projects, we frequently encountered the need to retrieve data from data sources, typically databases, in response to natural language queries.

The standard approach to this issue involves using the text-to-SQL technique. While this method is powerful, it is also complex and challenging to control. Often, the results were unsatisfactory because the Language Model lacked the necessary context to understand the specific requirements of the application and the business logic behind the data.

This led us to experiment with a more structured approach. In this method, the developer defines the specific use cases for the Language Model to handle, detailing the desired data format and the possible operations to retrieve this data. This approach proved to be more efficient, predictable, and easier to manage, making it simpler to integrate with the rest of the system.

Eventually, we decided to create a library that would allow us to use this approach in a more systematic way, and we made it open-source for the community.

## Installation

To install db-ally, execute the following command:

```bash
pip install dbally
```

Additionally, you can install one of our extensions to use specific features.

* `dbally[litellm]`: Use [100+ LLMs](https://docs.litellm.ai/docs/providers)
* `dbally[faiss]`: Use [Faiss](https://github.com/facebookresearch/faiss) indexes for similarity search
* `dbally[langsmith]`: Use [LangSmith](https://www.langchain.com/langsmith) for query tracking

```bash
pip install dbally[litellm,faiss,langsmith]
```

## License

db-ally is released under MIT license.

## How db-ally documentation is organized

- [Quickstart](https://db-ally.deepsense.ai/quickstart/) - Get started with db-ally in a few minutes
- [Concepts](https://db-ally.deepsense.ai/concepts/iql) - Understand the main concepts behind db-ally
- [How-to guides](https://db-ally.deepsense.ai/how-to/log_runs_to_langsmith) - Learn how to use db-ally in your projects
- [Tutorials](https://db-ally.deepsense.ai/tutorials) - Follow step-by-step tutorials to learn db-ally
- [API reference](https://db-ally.deepsense.ai/reference/collection) - Explore the underlying API of db-ally

## Roadmap

db-ally is actively developed and maintained by a core team at [deepsense.ai](https://deepsense.ai) and a community of contributors.

You can find a list of planned features and integrations in the [Roadmap](https://db-ally.deepsense.ai/about/roadmap).
