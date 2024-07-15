import asyncio
import logging
from enum import Enum
from typing import Callable, Dict

import hydra
import neptune
from bench.evaluator import Evaluator
from bench.metrics import (
    exact_match_iql,
    exact_match_sql,
    execution_accuracy,
    invalid_iql,
    invalid_sql,
    unsupported_iql,
    valid_efficiency_score,
    valid_iql,
    valid_sql,
)
from bench.pipelines import EndToEndEvaluationPipeline, EvaluationPipeline, IQLEvaluationPipeline, SQLEvaluationPipeline
from datasets import load_dataset
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


class EvaluationType(Enum):
    """
    Enum representing the type of evaluation.
    """

    E2E = "E2E"
    SQL = "SQL"
    IQL = "IQL"


EVALUATION_PIPELINES: Dict[str, EvaluationPipeline] = {
    EvaluationType.SQL.value: SQLEvaluationPipeline,
    EvaluationType.IQL.value: IQLEvaluationPipeline,
    EvaluationType.E2E.value: EndToEndEvaluationPipeline,
}

EVALUATION_METRICS: Dict[str, Callable] = {
    EvaluationType.IQL.value: {
        "em_iql": exact_match_iql,
        "valid_iql": valid_iql,
        "invalid_iql": invalid_iql,
        "unsupported_iql": unsupported_iql,
        "em_sql": exact_match_sql,
        "valid_sql": valid_sql,
        "invalid_sql": invalid_sql,
        "ex": execution_accuracy,
        "ves": valid_efficiency_score,
    },
    EvaluationType.SQL.value: {
        "em_sql": exact_match_sql,
        "valid_sql": valid_sql,
        "invalid_sql": invalid_sql,
        "ex": execution_accuracy,
        "ves": valid_efficiency_score,
    },
    EvaluationType.E2E.value: {
        "em_iql": exact_match_iql,
        "valid_iql": valid_iql,
        "invalid_iql": invalid_iql,
        "unsupported_iql": unsupported_iql,
        "em_sql": exact_match_iql,
        "valid_sql": valid_sql,
        "invalid_sql": invalid_sql,
        "ex": execution_accuracy,
        "ves": valid_efficiency_score,
    },
}


async def bench(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    dataset = load_dataset(config.data.path, split=config.data.split)
    dataset = dataset.filter(lambda x: x["db_id"] in config.data.db_ids and x["difficulty"] in config.data.difficulties)
    dataset = dataset.select(range(2))

    pipeline = EVALUATION_PIPELINES[config.task.type](config)
    metrics = EVALUATION_METRICS[config.task.type]

    evaluator = Evaluator(task=config.task.type)
    results = await evaluator.compute(
        pipe=pipeline,
        data=dataset,
        metrics=metrics,
    )

    if config.neptune:
        run = neptune.init_run()
        run["sys/tags"].add(
            [
                EvaluationType.SQL.value,
                config.view_name,
                config.llm.model_name,
                *config.db_ids,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics"] = stringify_unsupported(results["metrics"])


@hydra.main(config_path="config", config_name="config", version_base="1.3.2")
def main(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    asyncio.run(bench(config))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
