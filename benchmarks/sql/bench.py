import asyncio
import logging
from enum import Enum
from pathlib import Path

import hydra
import neptune
from bench.evaluator import Evaluator
from bench.loaders import CollectionDataLoader, IQLViewDataLoader, SQLViewDataLoader
from bench.metrics import (
    AggregationAccuracy,
    ExecutionAccuracy,
    FilteringAccuracy,
    FilteringPrecision,
    FilteringRecall,
    IQLAggregationCorrectness,
    IQLAggregationParseability,
    IQLFiltersAccuracy,
    IQLFiltersCorrectness,
    IQLFiltersParseability,
    IQLFiltersPrecision,
    IQLFiltersRecall,
    MetricSet,
    SQLExactMatch,
    ViewSelectionAccuracy,
    ViewSelectionPrecision,
    ViewSelectionRecall,
)
from bench.pipelines import CollectionEvaluationPipeline, IQLViewEvaluationPipeline, SQLViewEvaluationPipeline
from bench.utils import save
from hydra.core.hydra_config import HydraConfig
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
log = logging.getLogger(__name__)


class EvaluationType(Enum):
    """
    Enum representing the evaluation type.
    """

    IQL = "IQL_VIEW"
    SQL = "SQL_VIEW"
    E2E = "COLLECTION"


EVALUATION_DATALOADERS = {
    EvaluationType.IQL.value: IQLViewDataLoader,
    EvaluationType.SQL.value: SQLViewDataLoader,
    EvaluationType.E2E.value: CollectionDataLoader,
}

EVALUATION_PIPELINES = {
    EvaluationType.IQL.value: IQLViewEvaluationPipeline,
    EvaluationType.SQL.value: SQLViewEvaluationPipeline,
    EvaluationType.E2E.value: CollectionEvaluationPipeline,
}

EVALUATION_METRICS = {
    EvaluationType.IQL.value: MetricSet(
        AggregationAccuracy,
        FilteringAccuracy,
        FilteringPrecision,
        FilteringRecall,
        IQLAggregationParseability,
        IQLAggregationCorrectness,
        IQLFiltersAccuracy,
        IQLFiltersPrecision,
        IQLFiltersRecall,
        IQLFiltersParseability,
        IQLFiltersCorrectness,
        ExecutionAccuracy,
    ),
    EvaluationType.SQL.value: MetricSet(
        SQLExactMatch,
        ExecutionAccuracy,
    ),
    EvaluationType.E2E.value: MetricSet(
        AggregationAccuracy,
        FilteringAccuracy,
        FilteringPrecision,
        FilteringRecall,
        IQLAggregationParseability,
        IQLAggregationCorrectness,
        IQLFiltersAccuracy,
        IQLFiltersPrecision,
        IQLFiltersRecall,
        IQLFiltersParseability,
        IQLFiltersCorrectness,
        ViewSelectionAccuracy,
        ViewSelectionPrecision,
        ViewSelectionRecall,
        SQLExactMatch,
        ExecutionAccuracy,
    ),
}


async def bench(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    log.info("Starting evaluation: %s", config.setup.name)

    dataloader = EVALUATION_DATALOADERS[config.setup.name](config)
    pipeline = EVALUATION_PIPELINES[config.setup.name](config)
    metrics = EVALUATION_METRICS[config.setup.name](config)

    evaluator = Evaluator(config.setup.name)
    results = await evaluator.compute(
        pipeline=pipeline,
        dataloader=dataloader,
        metrics=metrics,
    )

    log.info("Evaluation finished. Saving results...")

    output_dir = Path(HydraConfig.get().runtime.output_dir)
    metrics_file = output_dir / "metrics.json"
    results_file = output_dir / "results.json"

    save(metrics_file, metrics=results["metrics"], time_perf=results["time_perf"])
    save(results_file, results=results["results"])

    log.info("Evaluation results saved under directory: %s", output_dir)

    if config.neptune:
        run = neptune.init_run()
        run["sys/tags"].add(
            [
                config.setup.name,
                *config.data.db_ids,
                *config.data.difficulties,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics"] = stringify_unsupported(results["metrics"])
        run["evaluation/time_perf"] = stringify_unsupported(results["time_perf"])
        run["evaluation/metrics.json"].upload(metrics_file.as_posix())
        run["evaluation/results.json"].upload(results_file.as_posix())


@hydra.main(config_path="config", config_name="config", version_base="3.2")
def main(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    asyncio.run(bench(config))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
