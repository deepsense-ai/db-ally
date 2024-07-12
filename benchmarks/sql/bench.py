import asyncio
from enum import Enum
from typing import Callable, Dict

import hydra
import neptune
from datasets import load_dataset
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from pipelines import TextToIQLEvaluationPipeline, TextToSQLEvaluationPipeline
from saving import save


class EvaluationType(Enum):
    """
    Enum representing the type of evaluation.
    """

    E2E = "e2e"
    SQL = "sql"
    IQL = "iql"


async def bench_iql(config: DictConfig) -> None:
    """
    Runs IQL evaluation for a single dataset defined in hydra config.

    Args:
        config: hydra config, loads automatically from path passed on to the decorator.
    """
    logger.info(f"Running IQL predictions for dataset: {config.dataset_path} and view: {config.view_name}.")

    dataset = load_dataset(config.dataset_path, split=config.split)
    dataset = dataset.filter(lambda x: x["db_id"] in config.db_ids and x["difficulty"] in config.difficulties)
    dataset = dataset.select(range(1))

    pipe = TextToIQLEvaluationPipeline(config)
    metrics, results = await pipe(dataset)

    output_file = save("./evals/", metrics=metrics, results=results)
    logger.info(f"IQL evaluation metrics and predictions saved under directory: {output_file}.")

    if config.neptune.run:
        run = neptune.init_run(project=config.neptune.project)
        run["sys/tags"].add(
            [
                EvaluationType.IQL.value,
                config.view_name,
                config.llm.model_name,
                *config.db_ids,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}.")


async def bench_sql(config: DictConfig) -> None:
    """
    Runs Text2SQL evaluation for a single dataset defined in hydra config.

    Args:
        config: hydra config, loads automatically from path passed on to the decorator
    """
    logger.info(f"Running SQL predictions for dataset: {config.dataset_path} and view: {config.view_name}.")

    dataset = load_dataset(config.dataset_path, split=config.split)
    dataset = dataset.filter(lambda x: x["db_id"] in config.db_ids and x["difficulty"] in config.difficulties)
    dataset = dataset.select(range(1))

    pipe = TextToSQLEvaluationPipeline(config)
    metrics, results = await pipe(dataset)

    output_file = save("./evals/", metrics=metrics, results=results)
    logger.info(f"IQL evaluation metrics and predictions saved under directory: {output_file}.")

    if config.neptune.run:
        run = neptune.init_run(project=config.neptune.project)
        run["sys/tags"].add(
            [
                EvaluationType.SQL.value,
                config.view_name,
                config.llm.model_name,
                *config.db_ids,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}.")


async def bench(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    evaluators_factory: Dict[str, Callable] = {
        EvaluationType.SQL.value: bench_sql,
        EvaluationType.IQL.value: bench_iql,
    }
    common_config = {k: v for k, v in config.items() if k not in evaluators_factory}
    for evaluation_type, eval_func in evaluators_factory.items():
        if evaluation_type in config:
            for dataset_config in config[evaluation_type].values():
                await eval_func(DictConfig({**common_config, **dataset_config}))


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    asyncio.run(bench(config))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
