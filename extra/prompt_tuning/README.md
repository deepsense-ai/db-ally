# Prompt tuning

This folder contains scripts for prompt tuning and evaluation. Prompts (programs) used in dbally:

- `FilteringAssessor` - assesses whether a question requires filtering.
- `AggregationAssessor` - assesses whether a question requires aggregation.

All evaluations are run on a dev split of the [BIRD](https://bird-bench.github.io/) dataset. For now, one configuration is available to run the suite against the `superhero` database.

## Usage

### Train new prompts

Tune `filtering-assessor` prompt on base signature using [COPRO](https://dspy-docs.vercel.app/docs/deep-dive/teleprompter/signature-optimizer#how-copro-works) optimizer on the `superhero` database with `gpt-3.5-turbo`:

```bash
python train.py prompt/type=filtering-assessor prompt/signature=baseline prompt/program=predict
```

Change optimizer to [MIPRO](https://dspy-docs.vercel.app/docs/cheatsheet#mipro):

```bash
python train.py prompt/type=filtering-assessor prompt/signature=baseline prompt/program=predict optimizer=mipro
```

Train multiple prompts:

```bash
python train.py --multirun \
    prompt/type=filtering-assessor \
    prompt/signature=baseline \
    prompt/program=predict,cot
```

Tweak optimizer params to get different results:

```bash
python train.py \
    optimizer=copro \
    optimizer.params.breadth=2 \
    optimizer.params.depth=3 \
    optimizer.params.init_temperature=1.0
```

### Evaluate prompts

Run evalution of filtering assessor baseline on the `superhero` database with `gpt-3.5-turbo`:

```bash
python evaluate.py prompt/type=filtering-assessor prompt/signature=baseline prompt/program=predict
```

Test multiple prompts:

```bash
python evaluate.py --multirun \
    prompt/type=filtering-assessor \
    prompt/signature=baseline \
    prompt/program=predict,cot
```

```bash
python evaluate.py --multirun \
    prompt/type=aggregation-assessor \
    prompt/signature=baseline \
    prompt/program=predict,cot
```

Compare prompt performance on multiple LLMs:

```bash
python evaluate.py --multirun \
    prompt/type=filtering-assessor \
    prompt/signature=baseline \
    prompt/program=predict \
    llm=gpt-3.5-turbo,claude-3.5-sonnet
```

#### Log to Neptune

Before running the evaluation with Neptune, configure the following environment variables:

```bash
export NEPTUNE_API_TOKEN="API_TOKEN"
export NEPTUNE_PROJECT="WORKSPACE_NAME/PROJECT_NAME"
```

Export evaluation results to Neptune:

```bash
python evaluate.py neptune=True
```
