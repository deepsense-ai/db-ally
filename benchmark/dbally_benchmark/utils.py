import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional, Union

from neptune.metadata_containers import Run


def load_data(
    file_path: Union[str, Path],
    encoding: Optional[str] = None,
) -> str:
    """
    Load data from a file.

    Args:
        file_path: Path of the data.
        encoding: Encoding of the input file.

    Returns:
        String read from the file.
    """

    with open(file_path, encoding=encoding) as file_handle:
        return file_handle.read()


def get_datetime_str() -> str:
    """
    Obtain a string representing current datetime.

    Returns:
        String representation of the current datetime.
    """
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def batch(iterable: Any, per_batch: int = 1) -> Iterator:
    """
    Splits an list into batches of a specified size.

    Args:
        iterable: The iterable to be batched.
        per_batch: The number of elements per batch. Default is 1.

    Yields:
        A generator that yields batches of elements from the original iterable.
    """

    length = len(iterable)
    for ndx in range(0, length, per_batch):
        yield iterable[ndx : min(ndx + per_batch, length)]


def set_up_gitlab_metadata(run: Run) -> Run:
    """
    Set up GitLab metadata for the Neptune run.

    Args:
        run: Neptune run object

    Returns:
        Neptune run object with GitLab metadata set up.
    """

    merge_request_project_url = os.getenv("CI_MERGE_REQUEST_PROJECT_URL")
    merge_request_iid = os.getenv("CI_MERGE_REQUEST_IID")
    merge_request_sha = os.getenv("CI_COMMIT_SHA")

    run["merge_request_url"] = f"{merge_request_project_url}/-/merge_requests/{merge_request_iid}"
    run["merge_request_sha"] = merge_request_sha

    return run
