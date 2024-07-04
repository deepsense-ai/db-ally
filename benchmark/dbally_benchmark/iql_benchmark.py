import asyncio
import json
import os
from pathlib import Path
from typing import Any, List

import hydra
import neptune
from dbally_benchmark.config import BenchmarkConfig
from dbally_benchmark.constants import VIEW_REGISTRY, EvaluationType, ViewName
from dbally_benchmark.dataset.bird_dataset import BIRDDataset, BIRDExample
from dbally_benchmark.iql.iql_result import IQLResult
from dbally_benchmark.iql.metrics import calculate_dataset_metrics
from dbally_benchmark.paths import PATH_EXPERIMENTS
from dbally_benchmark.utils import batch, get_datetime_str, set_up_gitlab_metadata
from hydra.utils import instantiate
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from sqlalchemy import create_engine

from dbally.audit.event_tracker import EventTracker
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.prompt import IQL_GENERATION_TEMPLATE, UnsupportedQueryError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.views.structured import BaseStructuredView


async def _run_iql_for_single_example(
    example: BIRDExample, view: BaseStructuredView, iql_generator: IQLGenerator
) -> IQLResult:
    filter_list = view.list_filters()
    event_tracker = EventTracker()

    try:
        iql_filters = await iql_generator.generate_iql(
            question=example.question,
            filters=filter_list,
            event_tracker=event_tracker,
        )
    except UnsupportedQueryError:
        return IQLResult(question=example.question, iql_filters="UNSUPPORTED_QUERY", exception_raised=True)

    return IQLResult(question=example.question, iql_filters=str(iql_filters), exception_raised=False)


async def run_iql_for_dataset(
    dataset: BIRDDataset, view: BaseStructuredView, iql_generator: IQLGenerator
) -> List[IQLResult]:
    """
    Runs IQL predictions for a dataset.

    Args:
        dataset: The dataset containing questions to be transformed into IQL queries.
        view: The view used to generate IQL.
        iql_generator: IQL generator.

    Returns:
        A list of IQLResult objects representing the predictions.
    """

    results: List[IQLResult] = []

    for group in batch(dataset, 5):
        current_results = await asyncio.gather(
            *[_run_iql_for_single_example(example, view, iql_generator) for example in group]
        )
        results = [*current_results, *results]

    return results


async def evaluate(cfg: DictConfig) -> Any:
    """
    Runs IQL evaluation for a single dataset defined in hydra config.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator

    Raises:
        ValueError: If view_name defined in hydra config is not supported.
        ValueError: If model_name is not supported (at the
        moment only OpenAI's model are supported).
    """

    output_dir = PATH_EXPERIMENTS / cfg.output_path / get_datetime_str()
    output_dir.mkdir(exist_ok=True, parents=True)
    cfg = instantiate(cfg)
    benchmark_cfg = BenchmarkConfig()

    view_name = cfg.view_name
    allowed_views = [view.value for view in ViewName]
    if view_name not in allowed_views:
        raise ValueError(f"View {view_name} not supported. Available views: {allowed_views}")

    engine = create_engine(benchmark_cfg.pg_connection_string + f"/{cfg.db_name}")
    view = VIEW_REGISTRY[ViewName(view_name)](engine)

    if cfg.model_name.startswith("local/"):
        llm = LocalLLM(model_name=cfg.model_name.split("/", 1)[1], api_key=benchmark_cfg.hf_api_key)
    else:
        llm = LiteLLM(api_key=benchmark_cfg.openai_api_key, model_name=cfg.model_name)

    iql_generator = IQLGenerator(llm=llm)

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=benchmark_cfg.neptune_project,
            api_token=benchmark_cfg.neptune_api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        tags = list(cfg.neptune.get("tags", [])) + [EvaluationType.IQL.value, view_name, cfg.model_name, cfg.db_name]
        run["sys/tags"].add(tags)

        if "CI_MERGE_REQUEST_IID" in os.environ:
            run = set_up_gitlab_metadata(run)

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running IQL predictions for dataset: {cfg.dataset_path} and view: {view_name}")
    evaluation_dataset = BIRDDataset.from_json_file(
        Path(cfg.dataset_path), difficulty_levels=cfg.get("difficulty_levels")
    )
    dbally_results = await run_iql_for_dataset(dataset=evaluation_dataset, view=view, iql_generator=iql_generator)
    valid_dbally_results = [result for result in dbally_results if not result.exception_raised]
    unsupported_query_error = (len(dbally_results) - len(valid_dbally_results)) / len(dbally_results)

    with open(output_dir / results_file_name, "w", encoding="utf-8") as outfile:
        json.dump([result.model_dump() for result in dbally_results], outfile, indent=4)

    logger.info("Calculating metrics")
    metrics = await calculate_dataset_metrics(dbally_results, view.list_filters())
    metrics = {**metrics, "unsupported_query_error": unsupported_query_error}

    with open(output_dir / metrics_file_name, "w", encoding="utf-8") as outfile:
        json.dump(metrics, outfile, indent=4)

    logger.info(f"IQL predictions saved under directory: {output_dir}")

    if run:
        run["config/iql_prompt_template"] = stringify_unsupported(IQL_GENERATION_TEMPLATE.chat)
        run[f"evaluation/{metrics_file_name}"].upload((output_dir / metrics_file_name).as_posix())
        run[f"evaluation/{results_file_name}"].upload((output_dir / results_file_name).as_posix())
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}")


@hydra.main(version_base=None, config_path="experiment_config", config_name="evaluate_iql_config")
def main(cfg: DictConfig):
    """
    Runs IQL evaluation for a single dataset defined in hydra config.
    The following metrics are calculated during evaluation: valid IQL,
    ratio of hallucinated filters and ratio of IQLs contained syntax error.

    Args:
        cfg: hydra config, loads automatically from path passed on to the decorator.
    """

    asyncio.run(evaluate(cfg))


if __name__ == "__main__":
    main()  # pylint: disable=E1120
