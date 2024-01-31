from pathlib import Path
from typing import Optional, Union


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
