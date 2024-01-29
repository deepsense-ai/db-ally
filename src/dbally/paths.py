from pathlib import Path
from typing import Union

import dbally

PATH_PACKAGE = Path(dbally.__file__).parent
PATH_ROOT = PATH_PACKAGE.parent.parent
PATH_EXPERIMENTS = PATH_ROOT / "experiments"
PATH_DATA = PATH_ROOT / "data"
PATH_SCHEMAS = PATH_DATA / "schemas"


def resolve_path_if_not_absolute(path: Union[str, Path], base_path: Union[str, Path]) -> Path:
    """Resolve path if it is not absolute.

    Args:
        path: Path to be resolved.
        base_path: Relative path to be appended if path not absolute.

    Returns:
        Path relative to base path."""

    path = Path(path)
    if path.is_absolute():
        return path
    return Path(base_path) / path
