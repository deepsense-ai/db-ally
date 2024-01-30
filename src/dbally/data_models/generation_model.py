from dataclasses import dataclass


@dataclass
class GenerationModelConfig:
    """Data class with configuration of LLM instance"""

    model_name: str
