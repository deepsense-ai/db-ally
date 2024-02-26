import asyncio
import json
import os
from pathlib import Path
from typing import Any, List

import asyncpg
import hydra
import neptune
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

import dbally
from dbally._collection import Collection
from dbally.data_models.prompts.iql_prompt_template import default_iql_template
from dbally.data_models.prompts.view_selector_prompt_template import default_view_selector_template
from dbally.db_connectors.pgsql_db import PGSqlConnector
from dbally.utils.errors import NoViewFoundError, UnsupportedQueryError
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.paths import PATH_EXPERIMENTS
from dbally_benchmark.text2sql.dataset import Text2SQLDataset, Text2SQLExample, Text2SQLResult
from dbally_benchmark.text2sql.metrics import calculate_dataset_metrics
from dbally_benchmark.text2sql.views import SuperheroCountByPowerView, SuperheroView
from dbally_benchmark.utils import batch, get_datetime_str


async def _run_dbally_for_single_example(example: Text2SQLExample, collection: Collection) -> Text2SQLResult:
    try:
        response = await collection.ask(example.question)
    except UnsupportedQueryError:
        response = "UnsupportedQueryError"
    except NoViewFoundError:
        response = "NoViewFoundError"
    except Exception:  # pylint: disable=broad-exception-caught
        response = "Error"

    return Text2SQLResult(
        db_id=example.db_id, question=example.question, ground_truth_sql=example.SQL, predicted_sql=response
    )


async def run_dbally_for_dataset(dataset: Text2SQLDataset, collection: Collection) -> List[Text2SQLResult]:
    """
    Transforms questions into SQL queries using a IQL approach.

    Args:
        dataset: The dataset containing questions to be transformed into SQL queries.
        collection: Container for a set of views used by db-ally.

    Returns:
        A list of Text2SQLResult objects representing the predictions.
    """

    results: List[Text2SQLResult] = []

    for group in batch(dataset, 5):
        current_results = await asyncio.gather(
            *[_run_dbally_for_single_example(example, collection) for example in group]
        )
        results = [*current_results, *results]

    return results


async def evaluate(cfg: DictConfig) -> Any:
    """
    Runs db-ally evaluation for a single dataset defined in hydra config.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator
    """

    output_dir = PATH_EXPERIMENTS / cfg.output_path / get_datetime_str()
    output_dir.mkdir(exist_ok=True, parents=True)
    cfg = instantiate(cfg)
    benchmark_cfg = BenchmarkConfig()

    connection_pool = await asyncpg.create_pool(dsn=benchmark_cfg.pg_conn_string)
    db_connector = PGSqlConnector(connection_pool=connection_pool)

    if "gpt" in benchmark_cfg.model_name:
        dbally.use_openai_llm(
            model_name="gpt-4",
            openai_api_key=benchmark_cfg.openai_api_key,
        )

    superheros_db = dbally.create_collection("superheros_db")
    superheros_db.add(SuperheroView)
    superheros_db.add(SuperheroCountByPowerView)

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["sys/tags"].add(list(cfg.neptune.tags))
        run["config"] = stringify_unsupported(cfg)

        if "CI_MERGE_REQUEST_IID" in os.environ:
            merge_request_project_url = os.getenv("CI_MERGE_REQUEST_PROJECT_URL")
            merge_request_iid = os.getenv("CI_MERGE_REQUEST_IID")
            merge_request_sha = os.getenv("CI_COMMIT_SHA")

            run["merge_request_url"] = f"{merge_request_project_url}/-/merge_requests/{merge_request_iid}"
            run["merge_request_sha"] = merge_request_sha

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running db-ally predictions for dataset {cfg.dataset_path}")
    evaluation_dataset = Text2SQLDataset.from_json_file(
        Path(cfg.dataset_path), db_ids=cfg.db_ids, difficulty_levels=cfg.difficulty_levels
    )
    dbally_results = await run_dbally_for_dataset(dataset=evaluation_dataset, collection=superheros_db)

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in dbally_results], outfile, indent=4)

    logger.info("Calculating metrics")
    metrics = await calculate_dataset_metrics(dbally_results, db_connector)

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile, indent=4)

    logger.info(f"db-ally predictions saved under directory: {output_dir}")

    if run:
        run["config/iql_prompt_template"] = stringify_unsupported(default_iql_template.chat)
        run["config/view_selection_prompt_template"] = stringify_unsupported(default_view_selector_template.chat)
        run["config/iql_prompt_template"] = stringify_unsupported(default_iql_template)
        run[f"evaluation/{metrics_file_name}"].upload((output_dir / metrics_file_name).as_posix())
        run[f"evaluation/{results_file_name}"].upload((output_dir / results_file_name).as_posix())
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info("Evaluation results logged to neptune")

    await connection_pool.close()


@hydra.main(version_base=None, config_path="experiment_config", config_name="evaluate_dbally_config")
def main(cfg: DictConfig):
    """
    Runs db-ally evaluation for a single dataset defined in hydra config.
    The following metrics are calculated during evaluation: exact match, valid SQL,
    execution accuracy and valid efficiency score.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator.
    """

    asyncio.run(evaluate(cfg))


if __name__ == "__main__":
    main()  # pylint: disable=E1120
