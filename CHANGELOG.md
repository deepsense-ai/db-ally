# Changelog

## v0.3.0 (2024-06-14)

### Feature

* Added text2sql views code generation (#40) ([`4284344`](https://github.com/deepsense-ai/db-ally/commit/42843443f42209955f7dc2273a3cdafb4a0c44ae))

* Added gradio adapter for interactive environment to test db-ally views / collections (#39)

### Documentation

* Added documentation for freeform views (#45) ([`825b8fe`](https://github.com/deepsense-ai/db-ally/commit/825b8fefd44bf74c80cdbc3eda304edc983fc8e9))

### Fix

* Fixed broken links in documentation ([`f5ffb6a`](https://github.com/deepsense-ai/db-ally/commit/f5ffb6af9e9d6f865b02706699bf6da94c3d95c1))

### Refactor

* Moved ExecutionResult to collection (#46) ([`eae24da`](https://github.com/deepsense-ai/db-ally/commit/eae24da3baddce06dbda575b08ef49b748d3af31))

### Chore

* Trigger the documentation build workflow only on release (#43) ([`6a1bf1d`](https://github.com/deepsense-ai/db-ally/commit/6a1bf1d26f6a874af48ceeb85cf21c7eb8c80e39))

## v0.2.0 (2024-06-03)

### Feature

* Introduce static configuration for freeform text2sql views (#36)

* Added elastic store as a new SimilarityStore(#34)

* Added LiteLLM embeddings (#37) ([`2fb275f`](https://github.com/deepsense-ai/db-ally/commit/2fb275f0668fb7f981d21a6eaeae0b5effcb4acd))

* Added support to 100s of LLMs via LiteLMM (#35) ([`c06b11d`](https://github.com/deepsense-ai/db-ally/commit/c06b11df1afb0c8f536c06d2f4d3d83cfc53d1d6))

* Added logging of audit events for SimilarityIndexes (#33)

### Documentation

* Updated guides and API reference (#38) ([`bc912c1`](https://github.com/deepsense-ai/db-ally/commit/bc912c11744a6f4c60e87185342ba963a0783369))

* Updated project roadmap ([`adfd479`](https://github.com/deepsense-ai/db-ally/commit/adfd479a6bc47539395ddaaf625d7333488f874b))

### Chore

* Swapped version constant for a variable in setup.cfg (#22)

### Fix

* Fixed AttributeError in LangSmithEventHandler (#32) ([`c8cfe97`](https://github.com/deepsense-ai/db-ally/commit/c8cfe9759aa4beb6c3bea4ae519be4b4fd2b105a))

### Refactor

* Refactored prompt builder (#30) ([`61f1066`](https://github.com/deepsense-ai/db-ally/commit/61f10669c29575178817cd9766f3e8cc4f16c79f))

* Refactored LLMOptions (#28) ([`3f5c4bf`](https://github.com/deepsense-ai/db-ally/commit/3f5c4bff2dcb0d354a744f1a7291e0f08a335867))

* Moved prompt templates to modules which use them (#26)

* Reorganized imports ([`e0f17a7`](https://github.com/deepsense-ai/db-ally/commit/e0f17a79f098549c4d98225101d5aa92733e503e))

* Replaced time measuring with monotonic clock (#25) ([`9b31299`](https://github.com/deepsense-ai/db-ally/commit/9b31299c5da9dc563beaff9762f2e85ed7bc1c4e))


## v0.1.0 (2024-04-25)

### Features

* Added text2sql freeform views (#20)

* Introduction of freeform views (#15)

* Integrated Chromadb as a SimilarityStore (#18)

### Documentation

* Added documentation for freeform views (#21)

* Fixed minor issues with classes names in documentation (#19)

### Chore

* Added automatic versioning with python-semantic-release (#16) ([`b7ffa25`](https://github.com/deepsense-ai/db-ally/commit/b7ffa255981ba3f5f22f7445a6d6415863575cdf))

## v0.0.2 (2024-04-17)

* Initial public release