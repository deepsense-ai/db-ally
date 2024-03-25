# FaissStore

The `FaissStore` class faciliates interaction with Meta Faiss. This component is used while mapping a user input to the closest matching value in the data source. In particular it  indexes values obtained via fetcher, allowing the system to find the closest match to the user's input.

!!! tip
    More details about Similarity Indexes can be found [here](../concepts/similarity_indexes.md).

::: dbally.similarity.faiss_store.FaissStore
