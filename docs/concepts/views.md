# Concept: Views

Views are a core concept in db-ally. They represent a way to define what you need from the LLM and connect it to the data source. The library provides two types of views:

* [Structured views](structured_views.md) *(recommended)* - these define a desired data structure and a set of operations that the LLM may use in response to natural language queries.
* [Freeform views](freeform_views.md) - these provide a more flexible way to define views, without a specific data structure or predefined operations.

Structured views are built on top of [IQL](iql.md), a simple language that acts as an abstraction layer between natural language and data source-specific query syntax, such as SQL. IQL allows the LLM to express complex queries in a more straightforward manner. In contrast, freeform views operate directly on the raw data source, using the data source's query language.

We consider **structured views** to be at the heart of db-ally. These enable the library's core benefits (consistency, security, efficiency, and portability), and provide a reliable interface for integration. Structured views are especially useful for applications with precise requirements in behavior or data format. For this reason, we recommend using structured views whenever possible.

Here are the differences between structured and freeform views, in terms of the core benefits of db-ally:

* **Consistency**: Structured views ensure predictable output formats, while freeform views offer more flexibility and can define views that do not require a fixed data structure. The former is easier to integrate with other systems and more predictable, while the latter provides more flexibility.
* **Security**: Structured views limit data source operations to those predefined by developers, whereas freeform views often allow the LLM to execute arbitrary operations on the data source. The former approach is considerably more secure (including protection against SQL injection attacks), whilst the latter approach is more flexible but requires developers to ensure the security of data sources outside of db-ally.
* **Efficiency**: Structured views provide [a layer of abstraction](iql.md) between the model and the data, which enables the LLM to focus on essential aspects, improving performance. Complex operations from the data source perspective can appear simple to the LLM. Conversely, freeform views can operate on the raw data source, which can be powerful but may also make it more challenging for the LLM to deliver good performance.
* **Portability**: Both structured and freeform views are typically defined in terms of a specific data source type and can be integrated with various database technologies and other data sources. However, freeform views integrate easier with data sources that already use a query language which the LLM can generate (like SQL), while structured views aren't similarly limited since they come with their query language (IQL).

A project might implement multiple views, of both types, each customised for different use cases. The LLM selects the most appropriate view corresponding to the specific natural language query. For further details, consider reading our article on [Collections](collections.md).