import asyncio
import logging
from pathlib import Path

import dspy
import dspy.teleprompt
import hydra
from omegaconf import DictConfig
from tuning import DATALOADERS, METRICS
from tuning.programs import PROGRAMS
from tuning.signatures import SIGNATURES

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("anthropic").setLevel(logging.ERROR)
log = logging.getLogger(__name__)


async def train(config: DictConfig) -> None:
    """
    Function running training for all datasets and training tasks defined in hydra config.

    Args:
        config: Hydra configuration.
    """
    signature_name = f"{config.prompt.type.id}{config.prompt.signature.id}"
    program_name = f"{config.prompt.type.id}{config.prompt.program.id}"

    log.info("Starting training: %s(%s) program with %s optimizer", program_name, signature_name, config.optimizer.name)

    dataloader = DATALOADERS[config.prompt.type.id](config)
    metric = METRICS[config.prompt.type.id]
    signature = SIGNATURES[signature_name]
    program = PROGRAMS[program_name](signature)

    dataset = await dataloader.load()

    lm = dspy.__dict__[config.llm.provider](model=config.llm.model_name)
    dspy.settings.configure(lm=lm)

    optimizer = dspy.teleprompt.__dict__[config.optimizer.name](metric=metric, **config.optimizer.params)
    compiled_program = optimizer.compile(
        student=program,
        trainset=dataset,
        eval_kwargs={
            "num_threads": config.num_threads,
            "display_progress": True,
        },
        **(config.optimizer.compile or {}),
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
