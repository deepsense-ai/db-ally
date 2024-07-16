import asyncio
import logging
from enum import Enum
from pathlib import Path
from typing import Dict

import hydra
import neptune
from bench.evaluator import Evaluator
from bench.metrics import (
    ExactMatchIQL,
    ExactMatchSQL,
    ExecutionAccuracy,
    HallucinatedIQL,
    MetricSet,
    UnsupportedIQL,
    ValidEfficiencyScore,
    ValidIQL,
    ValidSQL,
)
from bench.pipelines import (
    CollectionEvaluationPipeline,
    EvaluationPipeline,
    IQLViewEvaluationPipeline,
    SQLViewEvaluationPipeline,
)
from bench.utils import save
from datasets import load_dataset
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
log = logging.getLogger(__name__)


class EvaluationType(Enum):
    """
    Enum representing the type of evaluation.
    """

    COLLECTION = "COLLECTION"
    IQL_VIEW = "IQL-VIEW"
    SQL_VIEW = "SQL-VIEW"


EVALUATION_PIPELINES: Dict[str, EvaluationPipeline] = {
    EvaluationType.COLLECTION.value: CollectionEvaluationPipeline,
    EvaluationType.IQL_VIEW.value: IQLViewEvaluationPipeline,
    EvaluationType.SQL_VIEW.value: SQLViewEvaluationPipeline,
}

EVALUATION_METRICS: Dict[str, MetricSet] = {
    EvaluationType.COLLECTION.value: MetricSet(
        ExactMatchIQL,
        ExactMatchSQL,
        ValidIQL,
        ValidSQL,
        UnsupportedIQL,
        HallucinatedIQL,
        ExecutionAccuracy,
        ValidEfficiencyScore,
    ),
    EvaluationType.IQL_VIEW.value: MetricSet(
        ExactMatchIQL,
        ValidIQL,
        UnsupportedIQL,
        HallucinatedIQL,
        ExecutionAccuracy,
        ValidEfficiencyScore,
    ),
    EvaluationType.SQL_VIEW.value: MetricSet(
        ExactMatchSQL,
        ValidSQL,
        ExecutionAccuracy,
        ValidEfficiencyScore,
    ),
}


async def bench(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    log.info("Starting evaluation for component: %s.", config.component.type)

    dataset = load_dataset(config.data.path, split=config.data.split)
    dataset = dataset.filter(lambda x: x["db_id"] in config.data.db_ids and x["difficulty"] in config.data.difficulties)
    dataset = dataset.select(range(10, 20))

    pipeline = EVALUATION_PIPELINES[config.component.type](config)
    metrics = EVALUATION_METRICS[config.component.type](config)

    evaluator = Evaluator(config.component.type)
    results = await evaluator.compute(
        pipe=pipeline,
        data=dataset,
        metrics=metrics,
    )

    log.info("Evaluation finished. Saving results...")

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    metrics_file = output_dir / "metrics.json"
    results_file = output_dir / "results.json"

    save(metrics_file, metrics=results["metrics"], time_perf=results["time_perf"])
    save(results_file, results=results["results"])

    log.info("Evaluation results saved under directory: %s", output_dir)

    if config.neptune:
        run = neptune.init_run()
        run["sys/tags"].add(
            [
                config.component.type,
                config.data.id,
                config.llm.model_name,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/results.json"].upload(results_file.as_posix())
        run["evaluation/metrics.json"].upload(metrics_file.as_posix())
        run["evaluation/metrics"] = stringify_unsupported(results["metrics"])

        log.info("Evaluation results logged to neptune at %s", run.get_url())


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
