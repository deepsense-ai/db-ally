
---

<h1 align="center">db-ally</h1>

<p align="center">
    <em>Efficient, consistent and secure way to leverage various structured data sources via natural language interfaces</em>
</p>

---

**db-ally** is an LLM-powered tool for creating natural language interfaces to databases. While it occupies a similar space to the text-to-SQL solutions, its goals and methods are different. db-ally allows developers to outline specific use cases for the LLM to handle, detailing the desired data format and the possible operations to fetch this data.

db-ally effectively shields the complexity of the underlying database from the model, presenting only the essential information needed for solving the specific use cases. Instead of generating arbitrary SQL, the model is asked to generate responses in a simplified query language.


The benefits of db-ally can be described in terms of its four main characteristics:
* **Consistency**: db-ally ensures predictable output formats and confines operations to those predefined by developers, making it particularly well-suited for applications with precise requirements on their behavior or data format
* **Security**: db-ally prevents direct database access and arbitrary SQL execution, bolstering system safety
* **Efficiency**: db-ally hides most of the underlying database complexity, enabling the LLM to concentrate on essential aspects and improving performance
* **Portability**: db-ally introduces an abstraction layer between the model and the database, ensuring easy integration with various database technologies and data sources.

## Example

```python
print("Hello, World!")
```

## Installation

To install db-ally, execute the following command:

```bash
pip install dbally
```

Additionally, you can install one of our extensions to use specific features.

* `dbally[openai]`: Use OpenAI's models
* `dbally[faiss]`: Use FAISS indexes for similarity search
* `dbally[langsmith]`: Use langsmith for query tracking

```bash
pip install dbally[openai,faiss,langsmith]
```

## How db-ally documentation is organized


## Planned features

* **Feature 1**: ...
* **Feature 2**: ...
* **Feature 3**: ...



