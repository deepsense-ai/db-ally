import re
from dataclasses import dataclass
from typing import _GenericAlias  # type: ignore
from typing import List, Optional, Union

from dbally.similarity import AbstractSimilarityIndex


def parse_param_type(param_type: Union[type, _GenericAlias]) -> str:
    """
    Parses the type of a method parameter and returns a string representation of it.

    Args:
        param_type: type of the parameter

    Returns:
        str: string representation of the type
    """
    if param_type in {int, float, str, bool, list, dict, set, tuple}:
        return param_type.__name__
    if param_type.__module__ == "typing":
        return re.sub(r"\btyping\.", "", str(param_type))

    return str(param_type)


@dataclass
class MethodParamWithTyping:
    """
    Represents a method parameter with its type.
    """

    name: str
    type: Union[type, _GenericAlias]

    def __str__(self) -> str:
        return f"{self.name}: {parse_param_type(self.type)}"

    @property
    def similarity_index(self) -> Optional[AbstractSimilarityIndex]:
        """
        Returns the SimilarityIndex object if the type is annotated with it.
        """
        if hasattr(self.type, "__metadata__"):
            similarity_indexes = [meta for meta in self.type.__metadata__ if isinstance(meta, AbstractSimilarityIndex)]
            return similarity_indexes[0] if similarity_indexes else None

        return None


@dataclass
class ExposedFunction:
    """
    Represents a function exposed to the AI model.
    """

    name: str
    description: str
    parameters: List[MethodParamWithTyping]

    def __str__(self) -> str:
        base_str = f"{self.name}({', '.join(str(param) for param in self.parameters)})"

        if self.description != "":
            return f"{base_str} - {self.description}"

        return base_str
