import enum
from typing import Dict

import torch


class DataType(enum.Enum):
    """
    Class which represents torch.dtype used to load HuggingFace models.
    """

    FLOAT16 = "float16"
    FLOAT32 = "float32"
    BFLOAT16 = "bfloat16"


DTYPES_MAPPING: Dict[DataType, torch.dtype] = {
    DataType.FLOAT16: torch.float16,
    DataType.FLOAT32: torch.float32,
    DataType.BFLOAT16: torch.bfloat16,
}

DATASET_TEXT_FIELD = "messages"
