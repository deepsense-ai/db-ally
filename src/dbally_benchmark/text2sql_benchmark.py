import asyncio
import json
from pathlib import Path
from typing import Any, List

import asyncpg
import hydra
import neptune
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

from dbally.config import CoreConfig
from dbally.db_connectors.pgsql_db import PGSqlConnector
from dbally.paths import PATH_EXPERIMENTS
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.dataset import Text2SQLDataset, Text2SQLExample, Text2SQLResult
from dbally_benchmark.metrics import calculate_dataset_metrics
from dbally_benchmark.utils import batch, get_datetime_str


async def _run_text2sql_for_single_example(
    example: Text2SQLExample,
) -> str:
    # TODO: Replace with an actual model :).
    return Text2SQLResult(
        db_id=example.db_id, question=example.question, ground_truth_sql=example.SQL, predicted_sql=example.SQL
    )


async def run_text2sql_for_dataset(dataset: Text2SQLDataset) -> List[Text2SQLResult]:
    """
    Transforms questions into SQL queries using a Text2SQL model.

    Args:
        dataset: The dataset containing questions to be transformed into SQL queries.

    Returns:
        A list of Text2SQLResult objects representing the predictions.
    """

    results: List[Text2SQLResult] = []

    for group in batch(dataset, 5):
        current_results = await asyncio.gather(*[_run_text2sql_for_single_example(example) for example in group])
        results = [*current_results, *results]

    return results


async def evaluate(cfg: DictConfig) -> Any:
    """
    Runs Text2SQL evaluation for a single dataset defined in hydra config.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator
    """

    output_dir = PATH_EXPERIMENTS / cfg.output_path / get_datetime_str()
    output_dir.mkdir(exist_ok=True, parents=True)
    cfg = instantiate(cfg)
    benchmark_cfg = BenchmarkConfig()

    core_cfg = CoreConfig()
    connection_pool = await asyncpg.create_pool(dsn=core_cfg.database_conn_string)
    db_connector = PGSqlConnector(connection_pool=connection_pool)

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        run["sys/tags"].add(list(cfg.neptune.tags))

    logger.info(f"Running Text2SQ predictions for dataset {cfg.dataset_path}")
    evaluation_dataset = Text2SQLDataset.from_json_file(Path(cfg.dataset_path))
    text2sql_results = await run_text2sql_for_dataset(
        dataset=evaluation_dataset,
    )

    logger.info("Calculating metrics")
    metrics = await calculate_dataset_metrics(text2sql_results, db_connector)

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in text2sql_results], outfile)

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile)

    logger.info(f"Text2SQL predictions saved under directory: {output_dir}")

    if run:
        run[f"evaluation/{metrics_file_name}"].upload((output_dir / metrics_file_name).as_posix())
        run[f"evaluation/{results_file_name}"].upload((output_dir / results_file_name).as_posix())
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info("Evaluation results logged to neptune")


@hydra.main(version_base=None, config_path="../experiment_config", config_name="evaluate_text2sql_config")
def main(cfg: DictConfig):
    """
    Runs Text2SQL evaluation for a single dataset defined in hydra config.
    The following metrics are calculated during evaluation: exact match, valid SQL,
    execution accuracy and valid efficiency score.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator.
    """

    asyncio.run(evaluate(cfg))


if __name__ == "__main__":
    main()  # pylint: disable=E1120
