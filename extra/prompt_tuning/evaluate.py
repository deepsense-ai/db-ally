import asyncio
import logging
from pathlib import Path

import dspy
import hydra
import neptune
from dspy.evaluate import Evaluate
from neptune.utils import stringify_unsupported
from omegaconf import DictConfig
from tuning.loaders import IQLGenerationDataLoader
from tuning.metrics.iql import iql_dm
from tuning.programs import PROGRAMS
from tuning.utils import save, serialize_results

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("anthropic").setLevel(logging.ERROR)
log = logging.getLogger(__name__)


async def evaluate(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    log.info("Starting evaluation: %s", config.program.name)

    dataloader = IQLGenerationDataLoader(config)
    dataset = await dataloader.load()

    program = PROGRAMS[config.program.name]()

    lm = dspy.__dict__[config.llm.provider](model=config.llm.model_name)
    dspy.settings.configure(lm=lm)

    evaluator = Evaluate(
        devset=dataset,
        num_threads=32,
        display_progress=True,
        return_outputs=True,
    )
    metric, results = evaluator(program, metric=iql_dm)

    log.info("Evaluation finished. Saving results...")

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    results_file = output_dir / "results.json"
    save(results_file, results=serialize_results(results))

    log.info("Evaluation results saved under directory: %s", output_dir)

    if config.neptune:
        run = neptune.init_run()
        run["sys/tags"].add(
            [
                config.program.name,
                *config.data.db_ids,
                *config.data.difficulties,
            ]
        )
        run["config"] = stringify_unsupported(config)
        run["evaluation/metrics/ACC"] = stringify_unsupported(metric)
        run["evaluation/results.json"].upload(results_file.as_posix())


@hydra.main(config_path="config", config_name="config", version_base="3.2")
def main(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    asyncio.run(evaluate(config))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
