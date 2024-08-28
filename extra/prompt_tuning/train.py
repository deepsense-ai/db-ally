import asyncio
import logging
from pathlib import Path

import dspy
import hydra
from dspy.teleprompt import COPRO
from omegaconf import DictConfig
from tuning import DATALOADERS, METRICS
from tuning.programs import PROGRAMS

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("anthropic").setLevel(logging.ERROR)
log = logging.getLogger(__name__)


async def train(config: DictConfig) -> None:
    """
    Function running training for all datasets and training tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    log.info("Starting training: %s", config.program.name)

    dataloader = DATALOADERS[config.program.type](config)
    metric = METRICS[config.program.type]
    program = PROGRAMS[config.program.name]()

    dataset = await dataloader.load()

    lm = dspy.__dict__[config.llm.provider](model=config.llm.model_name)
    dspy.settings.configure(lm=lm)

    copro = COPRO(
        metric=metric,
        breadth=config.breadth,
        depth=config.depth,
        init_temperature=config.init_temperature,
    )
    compiled_program = copro.compile(
        student=program,
        trainset=dataset,
        eval_kwargs={
            "num_threads": config.num_threads,
            "display_progress": True,
        },
    )

    log.info("Training finished. Saving compiled program...")

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    program_file = output_dir / f"{program.__class__.__name__}Optimized.json"
    compiled_program.save(program_file)

    log.info("Compiled program saved under directory: %s", output_dir)


@hydra.main(config_path="config", config_name="train", version_base="3.2")
def main(config: DictConfig) -> None:
    """
    Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    asyncio.run(train(config))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
