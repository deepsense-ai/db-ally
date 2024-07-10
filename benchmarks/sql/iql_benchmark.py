import asyncio
import json
import os
from ast import Dict
from typing import Any, List

import hydra
import neptune
from constants import VIEW_REGISTRY, EvaluationType, ViewName
from datasets import Dataset, load_dataset
from hydra.utils import instantiate
from iql.iql_result import IQLResult
from iql.metrics import calculate_dataset_metrics
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from paths import PATH_EXPERIMENTS
from sqlalchemy import create_engine
from utils import get_datetime_str, set_up_gitlab_metadata

from dbally.audit.event_tracker import EventTracker
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.prompt import IQL_GENERATION_TEMPLATE, UnsupportedQueryError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.views.structured import BaseStructuredView


async def _run_iql_for_single_example(
    example: Dict,
    view: BaseStructuredView,
    iql_generator: IQLGenerator,
) -> IQLResult:
    filters = view.list_filters()
    event_tracker = EventTracker()

    try:
        predicted_iql = await iql_generator.generate_iql(
            question=example["question"],
            filters=filters,
            event_tracker=event_tracker,
        )
    except UnsupportedQueryError:
        return IQLResult(
            question=example["question"],
            ground_truth_iql=example["iql"],
            predicted_iql="UNSUPPORTED_QUERY",
            exception_raised=True,
        )
    except (SyntaxError, ValueError):
        return IQLResult(
            question=example["question"],
            ground_truth_iql=example["iql"],
            predicted_iql="",
            exception_raised=True,
        )

    return IQLResult(
        question=example["question"],
        ground_truth_iql=example["iql"],
        predicted_iql=str(predicted_iql),
        exception_raised=False,
    )


async def run_iql_for_dataset(
    dataset: Dataset,
    view: BaseStructuredView,
    iql_generator: IQLGenerator,
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

    for example in dataset:
        result = await _run_iql_for_single_example(example, view, iql_generator)
        results.append(result)

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
    cfg = instantiate(cfg)

    output_dir = PATH_EXPERIMENTS / cfg.output_path / get_datetime_str()
    output_dir.mkdir(exist_ok=True, parents=True)

    view_name = cfg.view_name
    allowed_views = [view.value for view in ViewName]
    if view_name not in allowed_views:
        raise ValueError(f"View {view_name} not supported. Available views: {allowed_views}")

    engine = create_engine(cfg.db_url)
    view = VIEW_REGISTRY[ViewName(view_name)](engine)

    if cfg.llm.model_name.startswith("local/"):
        llm = LocalLLM(
            model_name=cfg.llm.model_name.split("/", 1)[1],
            api_key=cfg.llm.api_key,
        )
    else:
        llm = LiteLLM(
            model_name=cfg.llm.model_name,
            api_key=cfg.llm.api_key,
        )

    iql_generator = IQLGenerator(llm=llm)

    run = None
    if cfg.neptune.log:
        run = neptune.init_run(
            project=cfg.neptune.project,
            api_token=cfg.neptune.api_token,
        )
        run["config"] = stringify_unsupported(cfg)
        tags = list(cfg.neptune.get("tags", [])) + [
            EvaluationType.IQL.value,
            view_name,
            cfg.llm.model_name,
            cfg.db_name,
        ]
        run["sys/tags"].add(tags)

        if "CI_MERGE_REQUEST_IID" in os.environ:
            run = set_up_gitlab_metadata(run)

    metrics_file_name, results_file_name = "metrics.json", "eval_results.json"

    logger.info(f"Running IQL predictions for dataset: {cfg.dataset_path} and view: {view_name}")

    dataset = load_dataset(cfg.dataset_path, split=cfg.split)
    dataset = dataset.filter(lambda x: x["db_id"] in cfg.db_ids and x["difficulty"] in cfg.difficulties)

    dbally_results = await run_iql_for_dataset(dataset=dataset, view=view, iql_generator=iql_generator)
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
