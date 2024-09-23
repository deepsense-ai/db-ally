import re
from dataclasses import dataclass
from typing import List, Optional, Type, Union, _GenericAlias  # type: ignore

from typing_extensions import _AnnotatedAlias, get_origin

from dbally.context.context import BaseCallerContext
from dbally.similarity import AbstractSimilarityIndex


@dataclass
class MethodParamWithTyping:
    """
    Represents a method parameter with its type.
    """

    name: str
    type: Union[type, _GenericAlias]

    def __str__(self) -> str:
        return f"{self.name}: {self._parse_type()}"

    @property
    def contexts(self) -> List[Type[BaseCallerContext]]:
        """
        Returns the contexts if the type is annotated with them.
        """
        return [arg for arg in getattr(self.type, "__args__", []) if issubclass(arg, BaseCallerContext)]

    @property
    def similarity_index(self) -> Optional[AbstractSimilarityIndex]:
        """
        Returns the SimilarityIndex object if the type is annotated with it.
        """
        return next(
            (arg for arg in getattr(self.type, "__metadata__", []) if isinstance(arg, AbstractSimilarityIndex)), None
        )

    def _parse_type(self) -> str:
        """
        Parses the type of a method parameter and returns a string representation of it.

        Returns:
            String representation of the type.
        """

        def _parse_type_inner(param_type: Union[type, _GenericAlias]) -> str:
            if get_origin(param_type) is Union:
                return " | ".join(_parse_type_inner(arg) for arg in self.type.__args__)

            if param_type.__module__ == "typing":
                return re.sub(r"\btyping\.", "", str(param_type))

            if issubclass(param_type, BaseCallerContext):
                return param_type.type_name

            if hasattr(param_type, "__name__"):
                return param_type.__name__

            if isinstance(self.type, _AnnotatedAlias):
                return _parse_type_inner(self.type.__origin__)

            return str(param_type)

        return _parse_type_inner(self.type)


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
