import asyncio
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Optional

import asyncpg
import hydra
import neptune
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

from dbally.constants import PromptType
from dbally.db_connectors.pgsql_db import PGSqlConnector
from dbally.llm_client.base import LLMClient
from dbally.llm_client.llm_client_factory import llm_client_factory
from dbally.paths import PATH_EXPERIMENTS, PATH_SCHEMAS
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.dataset import Text2SQLDataset, Text2SQLExample, Text2SQLResult
from dbally_benchmark.metrics import calculate_dataset_metrics
from dbally_benchmark.prompt_templates import PROMPT_TEMPLATES
from dbally_benchmark.utils import batch, get_datetime_str


def _load_db_schema(db_name: str, encoding: Optional[str] = None) -> str:
    db_schema_filename = db_name + ".sql"
    db_schema_path = PATH_SCHEMAS / db_schema_filename

    with open(db_schema_path, encoding=encoding) as file_handle:
        db_schema = file_handle.read()

    return db_schema


async def _run_text2sql_for_single_example(example: Text2SQLExample, llm_client: LLMClient) -> str:
    db_schema = _load_db_schema(example.db_id)

    prompt_template = PROMPT_TEMPLATES[llm_client.model_type][PromptType.TEXT2SQL]

    prompt = deepcopy(prompt_template)

    prompt[0]["content"] = prompt_template[0]["content"].format(schema=db_schema)
    prompt[1]["content"] = prompt_template[1]["content"].format(question=example.question)

    response = await llm_client.text_generation(prompt)

    return Text2SQLResult(
        db_id=example.db_id, question=example.question, ground_truth_sql=example.SQL, predicted_sql=response
    )


async def run_text2sql_for_dataset(dataset: Text2SQLDataset, llm_client: LLMClient) -> List[Text2SQLResult]:
    """
    Transforms questions into SQL queries using a Text2SQL model.

    Args:
        dataset: The dataset containing questions to be transformed into SQL queries.
        llm_client: LLM client.

    Returns:
        A list of Text2SQLResult objects representing the predictions.
    """

    results: List[Text2SQLResult] = []

    for group in batch(dataset, 5):
        current_results = await asyncio.gather(
            *[_run_text2sql_for_single_example(example, llm_client) for example in group]
        )
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

    connection_pool = await asyncpg.create_pool(dsn=benchmark_cfg.pg_conn_string)
    db_connector = PGSqlConnector(connection_pool=connection_pool)

    llm_client = llm_client_factory(benchmark_cfg.generation_model_type)

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        run["sys/tags"].add(list(cfg.neptune.tags))

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running Text2SQ predictions for dataset {cfg.dataset_path}")
    evaluation_dataset = Text2SQLDataset.from_json_file(Path(cfg.dataset_path), db_ids=cfg.db_ids)
    text2sql_results = await run_text2sql_for_dataset(dataset=evaluation_dataset, llm_client=llm_client)

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in text2sql_results], outfile, indent=4)

    logger.info("Calculating metrics")
    metrics = await calculate_dataset_metrics(text2sql_results, db_connector)

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile, indent=4)

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
