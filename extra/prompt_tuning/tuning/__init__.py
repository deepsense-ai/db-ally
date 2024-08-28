from enum import Enum

from .loaders import IQLGenerationDataLoader
from .metrics import aggregation_assess_acc, filtering_assess_acc


class ProgramType(Enum):
    """
    Program types.
    """

    FILTERING_ASSESSOR = "FILTERING_ASSESSOR"
    AGGREGATION_ASSESSOR = "AGGREGATION_ASSESSOR"


DATALOADERS = {
    ProgramType.FILTERING_ASSESSOR.value: IQLGenerationDataLoader,
    ProgramType.AGGREGATION_ASSESSOR.value: IQLGenerationDataLoader,
}

METRICS = {
    ProgramType.FILTERING_ASSESSOR.value: filtering_assess_acc,
    ProgramType.AGGREGATION_ASSESSOR.value: aggregation_assess_acc,
}
