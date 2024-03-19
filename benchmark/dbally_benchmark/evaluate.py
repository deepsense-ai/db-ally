import asyncio
from typing import Callable, Dict

import hydra
from dbally_benchmark.constants import EvaluationType
from dbally_benchmark.e2e_benchmark import evaluate as e2e_evaluate
from dbally_benchmark.iql_benchmark import evaluate as iql_evaluate
from dbally_benchmark.text2sql_benchmark import evaluate as text2sql_evaluate
from omegaconf import DictConfig


async def evaluate(cfg: DictConfig) -> None:
    """Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        cfg (DictConfig): Hydra config
    """
    evaluators_factory: Dict[str, Callable] = {
        EvaluationType.END2END.value: e2e_evaluate,
        EvaluationType.TEXT2SQL.value: text2sql_evaluate,
        EvaluationType.IQL.value: iql_evaluate,
    }

    common_cfg = {k: v for k, v in cfg.items() if k not in evaluators_factory}
    for evaluation_type, eval_func in evaluators_factory.items():
        if evaluation_type in cfg:
            for dataset_cfg in cfg[evaluation_type].values():
                await eval_func(DictConfig({**common_cfg, **dataset_cfg}))


@hydra.main(version_base=None, config_path="experiment_config", config_name="config")
def main(cfg: DictConfig):
    """Function running evaluation for all datasets and evaluation tasks defined in hydra config.

    Args:
        cfg (DictConfig): Hydra config"""
    asyncio.run(evaluate(cfg))


if __name__ == "__main__":
    main()  # pylint: disable=E1120
