"""Module to store useful paths."""
from pathlib import Path

import dbally_finetuning

PATH_SRC = Path(dbally_finetuning.__file__).parents[0]
PATH_CONFIG = PATH_SRC / "configs"
