# Roadmap

db-ally is actively developed and maintained by a core team at [deepsense.ai](https://deepsense.ai) and a community of contributors.

We are constantly working on new features and improvements.
If you have any ideas or suggestions, feel free to [open an issue](https://github.com/deepsense-ai/db-ally/issues) or [a pull request](https://github.com/deepsense-ai/db-ally/pulls).

Below you can find a list of planned features and integrations.

## Planned Features

- [ ] **Support analytical queries**: support for exposing operations beyond filtering.
- [ ] **Few-shot prompting configuration**: allow users to configure the few-shot prompting in View definition to
    improve IQL generation accuracy.
- [ ] **Request contextualization**: allow to provide extra context for db-ally runs, such as user asking the question.
- [ ] **OpenAI Assistants API adapter**: allow to embed db-ally into OpenAI's Assistants API to easily extend the
    capabilities of the assistant.
- [ ] **Langchain adapter**: allow to embed db-ally into Langchain applications.


## Integrations

Being agnostic to the underlying technology is one of the main goals of db-ally.
Below you can find a list of planned integrations.

### Data sources

- [x] Sqlalchemy
- [ ] Pandas DataFrame
- [ ] HTTP REST Endpoints
- [ ] GraphQL Endpoints

### LLMs

- [x] OpenAI models
- [ ] LLama-2
- [ ] Mistral / Mixtral
- [ ] VertexAI Gemini

### Vector stores

- [x] FAISS
- [ ] Chroma
- [ ] Weaviate
- [ ] Qdrant
- [ ] VertexAI Vector Search
- [ ] Milvus

### Query tracking

- [x] Langsmith
- [ ] OpenTelemetry
