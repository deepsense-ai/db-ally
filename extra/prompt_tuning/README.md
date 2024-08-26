# Prompt tuning

This folder contains scripts for prompt tuning and evaluation. Prompts (programs) used in dbally:

- `FILTERING_ASSESSOR` - assesses whether a question requires filtering.
- `AGGREGATION_ASSESSOR` - assesses whether a question requires aggregation.

All evaluations are run on a dev split of the [BIRD](https://bird-bench.github.io/) dataset. For now, one configuration is available to run the suite against the `superhero` database.

## Usage

Run evalution of filtering assessor baseline on the `superhero` database with `gpt-3.5-turbo`:

```bash
python evaluate.py program=filtering-assessor-baseline
```

Test multiple programs:

```bash
python evaluate.py --multirun program=filtering-assessor-baseline,filtering-assessor-cot
```

```bash
python evaluate.py --multirun program=aggregation-assessor-baseline,aggregation-assessor-cot
```

Compare prompt performance on multiple LLMs:

```bash
python evaluate.py --multirun program=filtering-assessor-baseline llm=gpt-3.5-turbo,claude-3.5-sonnet
```

### Log to Neptune

Before running the evaluation with Neptune, configure the following environment variables:

```bash
export NEPTUNE_API_TOKEN="API_TOKEN"
export NEPTUNE_PROJECT="WORKSPACE_NAME/PROJECT_NAME"
```

Export evaluation results to Neptune:

```bash
python evaluate.py neptune=True
```
