import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from datasets.utils.filelock import FileLock


def save(path_or_file: str, **data: Any) -> Path:
    """
    Saves results to a JSON file. Also saves system information such as current time and Python system information.

    Args:
        path_or_file: Path or file to store the file. If only a folder is provided
            the results file will be saved in the format `"result-%Y_%m_%d-%H_%M_%S.json"`.
        **data: The data to save.

    Returns:
        The path to the saved file.
    """
    current_time = datetime.now()
    print(type(current_time))

    file_path = _setup_path(path_or_file, current_time)

    data["_timestamp"] = current_time.isoformat()
    data["_python_version"] = sys.version
    data["_interpreter_path"] = sys.executable

    with FileLock(str(file_path) + ".lock"):
        with open(file_path, "w", encoding="utf8") as f:
            json.dump(data, f)

    try:
        os.remove(str(file_path) + ".lock")
    except FileNotFoundError:
        pass

    return file_path


def _setup_path(path_or_file: str, current_time: datetime) -> Path:
    path_or_file = Path(path_or_file)
    is_file = len(path_or_file.suffix) > 0
    if is_file:
        folder = path_or_file.parent
        file_name = path_or_file.name
    else:
        folder = path_or_file
        file_name = "result-" + current_time.strftime("%Y_%m_%d-%H_%M_%S") + ".json"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / file_name
