import asyncio
import json
import os
from functools import partial
from pathlib import Path
from typing import Any, List

import hydra
import neptune
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.constants import VIEW_REGISTRY, EvaluationType, ViewName
from dbally_benchmark.dataset.bird_dataset import BIRDDataset, BIRDExample
from dbally_benchmark.paths import PATH_EXPERIMENTS
from dbally_benchmark.text2sql.metrics import calculate_dataset_metrics
from dbally_benchmark.text2sql.text2sql_result import Text2SQLResult
from dbally_benchmark.utils import batch, get_datetime_str, set_up_gitlab_metadata
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from sqlalchemy import create_engine

import dbally
from dbally.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.iql_generator.prompt import IQL_GENERATION_TEMPLATE, UnsupportedQueryError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.view_selection.prompt import VIEW_SELECTION_TEMPLATE


async def _run_dbally_for_single_example(example: BIRDExample, collection: Collection) -> Text2SQLResult:
    try:
        result = await collection.ask(example.question, dry_run=True)
        sql = result.context["sql"]
    except UnsupportedQueryError:
        sql = "UnsupportedQueryError"
    except NoViewFoundError:
        sql = "NoViewFoundError"
    except Exception:  # pylint: disable=broad-exception-caught
        sql = "Error"

    return Text2SQLResult(
        db_id=example.db_id, question=example.question, ground_truth_sql=example.SQL, predicted_sql=sql
    )


async def run_dbally_for_dataset(dataset: BIRDDataset, collection: Collection) -> List[Text2SQLResult]:
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

    engine = create_engine(benchmark_cfg.pg_connection_string + f"/{cfg.db_name}")

    if cfg.model_name.startswith("local/"):
        llm = LocalLLM(api_key=benchmark_cfg.hf_api_key, model_name=cfg.model_name.split("/", 1)[1])
    else:
        llm = LiteLLM(
            model_name=cfg.model_name,
            api_key=benchmark_cfg.openai_api_key,
        )

    db = dbally.create_collection(cfg.db_name, llm)

    for view_name in cfg.view_names:
        view = VIEW_REGISTRY[ViewName(view_name)]
        db.add(view, partial(view, engine))

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        tags = list(cfg.neptune.get("tags", [])) + [EvaluationType.END2END.value, cfg.model_name, cfg.db_name]
        run["sys/tags"].add(tags)

        if "CI_MERGE_REQUEST_IID" in os.environ:
            run = set_up_gitlab_metadata(run)

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running db-ally predictions for dataset {cfg.dataset_path}")
    evaluation_dataset = BIRDDataset.from_json_file(
        Path(cfg.dataset_path), difficulty_levels=cfg.get("difficulty_levels")
    )
    dbally_results = await run_dbally_for_dataset(dataset=evaluation_dataset, collection=db)

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in dbally_results], outfile, indent=4)

    logger.info("Calculating metrics")
    metrics = calculate_dataset_metrics(dbally_results, engine)

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile, indent=4)

    logger.info(f"db-ally predictions saved under directory: {output_dir}")

    if run:
        run["config/iql_prompt_template"] = stringify_unsupported(IQL_GENERATION_TEMPLATE.chat)
        run["config/view_selection_prompt_template"] = stringify_unsupported(VIEW_SELECTION_TEMPLATE.chat)
        run["config/iql_prompt_template"] = stringify_unsupported(IQL_GENERATION_TEMPLATE)
        run[f"evaluation/{metrics_file_name}"].upload((output_dir / metrics_file_name).as_posix())
        run[f"evaluation/{results_file_name}"].upload((output_dir / results_file_name).as_posix())
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}")


@hydra.main(version_base=None, config_path="experiment_config", config_name="evaluate_e2e_config")
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
