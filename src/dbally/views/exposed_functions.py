from dataclasses import dataclass
from inspect import isclass
from typing import _GenericAlias  # type: ignore
from typing import Optional, Sequence, Type, Union

import typing_extensions as type_ext

from dbally.context.context import BaseCallerContext
from dbally.similarity import AbstractSimilarityIndex


def parse_param_type(param_type: Union[type, _GenericAlias, str]) -> str:
    """
    Parses the type of a method parameter and returns a string representation of it.

    Args:
        param_type: Type of the parameter.

    Returns:
        A string representation of the type.
    """

    # TODO consider using hasattr() to ensure correctness of the IF's below
    if isclass(param_type):
        return param_type.__name__

    # typing.Literal['aaa', 'bbb'] edge case handler
    # the args are strings not types thus isclass('aaa') is False
    # at the same type string has no __module__ property which causes an error
    if isinstance(param_type, str):
        return f"'{param_type}'"

    if param_type.__module__ in ["typing", "typing_extensions"]:
        type_args = type_ext.get_args(param_type)
        if type_args:
            param_name = param_type._name  # pylint: disable=protected-access
            if param_name is None:
                # workaround for typing.Literal, because: `typing.Literal['aaa', 'bbb']._name is None`
                # but at the same time: `type_ext.get_origin(typing.Literal['aaa', 'bbb'])._name == "Literal"`
                param_name = type_ext.get_origin(param_type)._name  # pylint: disable=protected-access

            args_str_repr = ", ".join(parse_param_type(arg) for arg in type_args)
            return f"{param_name}[{args_str_repr}]"

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
    parameters: Sequence[MethodParamWithTyping]
    context_class: Optional[Type[BaseCallerContext]] = None

    def __str__(self) -> str:
        base_str = f"{self.name}({', '.join(str(param) for param in self.parameters)})"

        if self.description != "":
            return f"{base_str} - {self.description}"

        return base_str
