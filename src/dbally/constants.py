from enum import Enum

from dbally.data_models.generation_model import GenerationModelConfig


class GenerationModel(str, Enum):
    """Enum representing generation model instance."""

    GPT4 = "GPT4"


GENERATION_MODEL_CONFIG = {GenerationModel.GPT4: GenerationModelConfig(model_name="gpt4")}
