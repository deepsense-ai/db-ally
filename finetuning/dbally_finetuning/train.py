# pylint: disable=C0116
import os
from datetime import datetime

import hydra
from dbally_finetuning.paths import PATH_CONFIG
from dbally_finetuning.trainer.iql_trainer import IQLTrainer


@hydra.main(config_name="config", config_path=str(PATH_CONFIG), version_base=None)
def main(config):
    output_dir = os.path.join(config.output_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(output_dir, exist_ok=True)

    iql_trainer = IQLTrainer(config, output_dir)
    iql_trainer.finetune()


if __name__ == "__main__":
    main()  # pylint: disable=E1120
