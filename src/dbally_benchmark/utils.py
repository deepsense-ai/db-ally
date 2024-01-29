from datetime import datetime
from typing import Iterator, List


def get_datetime_str() -> str:
    """
    Obtain a string representing current datetime.

    Returns:
        String representation of the current datetime.
    """
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def batch(iterable: List, per_batch: int = 1) -> Iterator:
    """
    Splits an list into batches of a specified size.

    Args:
        iterable: The list to be batched.
        per_batch: The number of elements per batch. Default is 1.

    Yields:
        A generator that yields batches of elements from the original iterable.
    """

    length = len(iterable)
    for ndx in range(0, length, per_batch):
        yield iterable[ndx : min(ndx + per_batch, length)]
