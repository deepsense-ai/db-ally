import asyncio
import json
import os
from pathlib import Path
from typing import Any, List, Optional

import hydra
import neptune
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.constants import EvaluationType
from dbally_benchmark.dataset.bird_dataset import BIRDDataset, BIRDExample
from dbally_benchmark.paths import PATH_EXPERIMENTS, PATH_SCHEMAS
from dbally_benchmark.text2sql.metrics import calculate_dataset_metrics
from dbally_benchmark.text2sql.prompt_template import TEXT2SQL_PROMPT_TEMPLATE
from dbally_benchmark.text2sql.text2sql_result import Text2SQLResult
from dbally_benchmark.utils import batch, get_datetime_str, set_up_gitlab_metadata
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from sqlalchemy import create_engine

from dbally.audit.event_tracker import EventTracker
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM


def _load_db_schema(db_name: str, encoding: Optional[str] = None) -> str:
    db_schema_filename = db_name + ".sql"
    db_schema_path = PATH_SCHEMAS / db_schema_filename

    with open(db_schema_path, encoding=encoding) as file_handle:
        db_schema = file_handle.read()

    return db_schema


async def _run_text2sql_for_single_example(example: BIRDExample, llm: LiteLLM) -> Text2SQLResult:
    event_tracker = EventTracker()

    db_schema = _load_db_schema(example.db_id)

    response = await llm.generate_text(
        TEXT2SQL_PROMPT_TEMPLATE, {"schema": db_schema, "question": example.question}, event_tracker=event_tracker
    )

    return Text2SQLResult(
        db_id=example.db_id, question=example.question, ground_truth_sql=example.SQL, predicted_sql=response
    )


async def run_text2sql_for_dataset(dataset: BIRDDataset, llm: LiteLLM) -> List[Text2SQLResult]:
    """
    Transforms questions into SQL queries using a Text2SQL model.

    Args:
        dataset: The dataset containing questions to be transformed into SQL queries.
        llm: LLM client.

    Returns:
        A list of Text2SQLResult objects representing the predictions.
    """

    results: List[Text2SQLResult] = []

    for group in batch(dataset, 5):
        current_results = await asyncio.gather(*[_run_text2sql_for_single_example(example, llm) for example in group])
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

    engine = create_engine(benchmark_cfg.pg_connection_string + f"/{cfg.db_name}")

    if cfg.model_name.startswith("local/"):
        llm = LocalLLM(model_name=cfg.model_name.split("/", 1)[1], api_key=benchmark_cfg.hf_api_key)
    else:
        llm = LiteLLM(
            api_key=benchmark_cfg.openai_api_key,
            model_name=cfg.model_name,
        )

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        tags = list(cfg.neptune.get("tags", [])) + [EvaluationType.TEXT2SQL.value, cfg.db_name, cfg.model_name]
        run["sys/tags"].add(tags)

        if "CI_MERGE_REQUEST_IID" in os.environ:
            run = set_up_gitlab_metadata(run)

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running Text2SQ predictions for dataset {cfg.dataset_path}")
    evaluation_dataset = BIRDDataset.from_json_file(
        Path(cfg.dataset_path), difficulty_levels=cfg.get("difficulty_levels")
    )
    text2sql_results = await run_text2sql_for_dataset(dataset=evaluation_dataset, llm=llm)

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in text2sql_results], outfile, indent=4)

    logger.info("Calculating metrics")
    metrics = calculate_dataset_metrics(text2sql_results, engine)

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile, indent=4)

    logger.info(f"Text2SQL predictions saved under directory: {output_dir}")

    if run:
        run["config/prompt_template"] = stringify_unsupported(TEXT2SQL_PROMPT_TEMPLATE.chat)
        run[f"evaluation/{metrics_file_name}"].upload((output_dir / metrics_file_name).as_posix())
        run[f"evaluation/{results_file_name}"].upload((output_dir / results_file_name).as_posix())
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}")


@hydra.main(version_base=None, config_path="experiment_config", config_name="evaluate_text2sql_config")
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
