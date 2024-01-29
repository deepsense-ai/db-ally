from enum import Enum


class PromptType(str, Enum):
    """Class representing prompt pattern type."""

    TEXT2SQL = "Text2SQL"


class GenerationModelType(str, Enum):
    """Class representing generation model type."""

    GPT4 = "GPT4"
