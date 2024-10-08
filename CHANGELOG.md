# Changelog

## v0.7.0 (2024-09-04)

### Feature

* feat(gradio): enhance gradio interface (#90) ([`8692637`](https://github.com/deepsense-ai/db-ally/commit/8692637d491385a2e6fe18bd0476c70dbd3997e5))

### Fix

* fix: pin griffe dependency ([`c562c01`](https://github.com/deepsense-ai/db-ally/commit/c562c014a38ed02f0a1df6f5bee2223610be5d5d))

## v0.6.0 (2024-09-02)

### Feature

* feat: aggregations in structured views (#62) ([`139ab9b`](https://github.com/deepsense-ai/db-ally/commit/139ab9be6514cb0777251efafc3e272cac00e6cd))

* feat(extra): prompt tuning (#79) ([`2714e7c`](https://github.com/deepsense-ai/db-ally/commit/2714e7c839137a9fc617270c086167d273a16f1a))

* feat(views): optional filtering for structured views (#78) ([`11a7b21`](https://github.com/deepsense-ai/db-ally/commit/11a7b21956ab33f47c1a9986deb6a5c154988579))

### Documentation

* docs(aggregations): structured view aggregations (#87) ([`9f6b5df`](https://github.com/deepsense-ai/db-ally/commit/9f6b5df380fe7a48a36eb3810a6712bc46d9b728))

* docs(quickstart): update quickstart (#88) ([`9a1e9d8`](https://github.com/deepsense-ai/db-ally/commit/9a1e9d8bcad5e124f3faa9a5798e8b2daefeee1a))

* docs: update logo (#86) ([`23e50ff`](https://github.com/deepsense-ai/db-ally/commit/23e50ff7159112dea3c1988eacbe85de3696628e))

### Refactor

* refactor(benchmarks): evaluation pipeline (#71) ([`cd2cece`](https://github.com/deepsense-ai/db-ally/commit/cd2cece73cb3ae2d4d5efe61cbfbec03c4968543))

* refactor(iql): add iql gen exception (#77) ([`90b0e66`](https://github.com/deepsense-ai/db-ally/commit/90b0e669394655c28e3256e24321cbeaea2a91c6))

### Chore

* chore: update changelog ([`0a22942`](https://github.com/deepsense-ai/db-ally/commit/0a22942451c80ee5d572805ac67981b6e96d96ae))

## v0.5.0 (2024-07-23)

### Feature

* feat: allow collection fallbacks (#59) ([`a2ef774`](https://github.com/deepsense-ai/db-ally/commit/a2ef7742be50502c0d8e35714cc6e585930e7d4a))

* feat: Add OpenTelemetry event handler (#70) ([`07d9b27`](https://github.com/deepsense-ai/db-ally/commit/07d9b2724010e13662f9a370d7406d3f6d57bb04))

* feat: implement global event handlers (#64) ([`221f6e1`](https://github.com/deepsense-ai/db-ally/commit/221f6e1a632c66b0579989676501ac559b0f5dbf))

### Chore

* chore: update roadmap ([`a448b01`](https://github.com/deepsense-ai/db-ally/commit/a448b0168c49ad62de1e6d25547cb680bbc91d3a))

* chore: changelog heading fix ([`b4bf9c3`](https://github.com/deepsense-ai/db-ally/commit/b4bf9c3a0185b79df0f6459dde896b620af83ce5))

* chore: changelog update after v0.4.0 ([`fde0884`](https://github.com/deepsense-ai/db-ally/commit/fde08849f2ecefa7ca452eadf3f2fed9f4b36265))

### Refactor

* refactor(iql): errors definition (#73) ([`ea687f8`](https://github.com/deepsense-ai/db-ally/commit/ea687f8e6efca02b5001d31342d5b5751a98aae9))


## v0.4.0 (2024-07-04)

### Feature

* Added support for local HuggingFace models (#61) ([`953d8a1`](https://github.com/deepsense-ai/db-ally/commit/953d8a1f3c39c624dcc3927e9dfb4df08121df35))

* Few-shot examples can be now injected into Structured / Freeform view generation prompts (#42) ([`d482638`](https://github.com/deepsense-ai/db-ally/commit/d4826385e95505c077a1c710feeba68ddcaef20c))

### Documentation

* Added docs explaining how to use AzureOpenAI (#55) ([`d890fec`](https://github.com/deepsense-ai/db-ally/commit/d890fecad38ed11d90a85e6472e64c81c607cf91))

### Fix

* Fixed a bug with natural language responder hallucination when no data is returned (#68) ([`e3fec18`](https://github.com/deepsense-ai/db-ally/commit/e3fec186cca0cace7db4b6e92da5b047a27dfa80))

### Chore

* Project was doggified 🦮 (#67) ([`a4fd411`](https://github.com/deepsense-ai/db-ally/commit/a4fd4115bc7884f5043a6839cfefdd36c97e94ab))

* `enhancment` label was replaced by `feature` ([`cd5bf7b`](https://github.com/deepsense-ai/db-ally/commit/cd5bf7b76b97e8d9e46ff872859ccd0ffdef859e))

## Refactor

* Refactor of prompt templates (#66) ([`6510bd8`](https://github.com/deepsense-ai/db-ally/commit/6510bd83923c83c69f082b63c722065fd0e7a3cd))

* Refactor audit module (#58) ([`9fd817f`](https://github.com/deepsense-ai/db-ally/commit/9fd817f3955e4e0c61da1cf9be44e9b6ac426c15))


## v0.3.1 (2024-06-17)

### Documentation

* Added about section to documentation (#50) ([`a32b3fe`](https://github.com/deepsense-ai/db-ally/commit/a32b3fe0cee2ee6ab94ceace701c158df5cf2dd4))

### Fix

* Fixed gradio interface crash on types that are not json serializable (#47) ([`f501156`](https://github.com/deepsense-ai/db-ally/commit/f501156ab75783b05a0a54af5c047702a53a0a36))

### Chore

* Added issue templates (#48) ([`fa76702`](https://github.com/deepsense-ai/db-ally/commit/fa767022c5ea5e49816321095fda4a20273995f9))

* Cleaned up changelog (#49) ([`6a3d08f`](https://github.com/deepsense-ai/db-ally/commit/6a3d08fc719e5a912ff3fd7effec732504230a27))

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