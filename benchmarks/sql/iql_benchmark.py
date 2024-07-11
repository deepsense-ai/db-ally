import asyncio

import hydra
import neptune
from constants import EvaluationType
from datasets import load_dataset
from loguru import logger
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from pipeline import TextToIQLEvaluationPipeline
from saving import save


@hydra.main(version_base=None, config_path="experiment_config", config_name="evaluate_iql_config")
async def evaluate(config: DictConfig) -> None:
    """
    Runs IQL evaluation for a single dataset defined in hydra config.

    Args:
        config: hydra config, loads automatically from path passed on to the decorator.
    """
    logger.info(f"Running IQL predictions for dataset: {config.dataset_path} and view: {config.view_name}.")
    dataset = load_dataset(config.dataset_path, split=config.split)
    dataset = dataset.filter(lambda x: x["db_id"] in config.db_ids and x["difficulty"] in config.difficulties)

    pipe = TextToIQLEvaluationPipeline(config)
    metrics, results = await pipe(dataset)

    output_file = save("./evals/", metrics=metrics, results=results)
    logger.info(f"IQL evaluation metrics and predictions saved under directory: {output_file}.")

    if config.neptune.log:
        run = neptune.init_run(
            project=config.neptune.project,
            api_token=config.neptune.api_token,
        )
        run["sys/tags"].add(
            [
                EvaluationType.IQL.value,
                config.view_name,
                config.llm.model_name,
                config.db_name,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics"] = stringify_unsupported(metrics)
        logger.info(f"Evaluation results logged to neptune at {run.get_url()}.")


if __name__ == "__main__":
    asyncio.run(evaluate())  # pylint: disable=E1120
