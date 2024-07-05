from pathlib import Path

# import sql

PATH_PACKAGE = Path(__file__).parent

PATH_ROOT = PATH_PACKAGE.parent.parent
PATH_EXPERIMENTS = PATH_ROOT / "experiments"
PATH_DATA = PATH_ROOT / "data"
PATH_SCHEMAS = PATH_DATA / "schemas"
