from dataclasses import dataclass
from inspect import isclass
from typing import _GenericAlias  # type: ignore
from typing import Generator, Iterable, Optional, Sequence, Type, Union

import typing_extensions as type_ext

from dbally.context.context import BaseCallerContext
from dbally.context.exceptions import BaseContextError, SuitableContextNotProvidedError
from dbally.similarity import AbstractSimilarityIndex


class TypeParsingError(ValueError):
    """
    Custo error raised when parsing a data type using `parse_param_type()` fails.
    """


def _parse_standard_type(param_type: Union[type_ext.Type, _GenericAlias]) -> str:
    """
    Generates string representation of a data type (or alias) being neither custom class or string.
    This function is primarily intended to parse types from consecutive modules:
    `builtins` (>= Python 3.9), `typing` and `typing_extensions`.

    Args:
        param_type: type or type alias.

    Returns:
        A string representation of the type.
    """

    # delegating large chunk of parsing code to this separate function prevents
    # pylint from raising R0911: too-many-return-statements

    param_name = param_type._name  # pylint: disable=protected-access
    if param_name is None:
        # workaround for typing.Literal, because: `typing.Literal['aaa', 'bbb']._name is None`
        # but at the same time: `type_ext.get_origin(typing.Literal['aaa', 'bbb'])._name == "Literal"`
        param_origin_type = type_ext.get_origin(param_type)
        if param_origin_type is None:
            # probably unnecessary hack ensuring
            raise TypeParsingError(f"Unable to parse: {str(param_type)}")

        param_name = param_origin_type._name  # pylint: disable=protected-access

    type_args = type_ext.get_args(param_type)
    if not type_args:
        return param_name

    parsed_args: Generator[str] = (parse_param_type(arg) for arg in type_args)
    if type_ext.get_origin(param_type) is Union:
        return " | ".join(parsed_args)

    parsed_args_concatanated = ", ".join(parsed_args)
    return f"{param_name}[{parsed_args_concatanated}]"


def parse_param_type(param_type: Union[type_ext.Type, _GenericAlias, str]) -> str:
    """
    Parses the type of a method parameter and returns a string representation of it.

    Args:
        param_type: Type of the parameter.

    Returns:
        A string representation of the type.
    """

    # TODO consider using hasattr() to ensure correctness of the IF's below
    if isclass(param_type):
        if issubclass(param_type, BaseCallerContext):
            # this mechanism ensures the LLM will be able to notice the relation between
            # the keyword-call specified in the prompt and the filter method signatures
            return BaseCallerContext.alias

        return param_type.__name__

    # typing.Literal['aaa', 'bbb'] edge case handler
    # the args are strings not types thus isclass('aaa') is False
    # at the same type string has no __module__ property which causes an error
    if isinstance(param_type, str):
        return f"'{param_type}'"

    if param_type.__module__ in ["builtins", "typing", "typing_extensions"]:
        return _parse_standard_type(param_type)

    # TODO add explicit support Generic types,
    # although they should be already handled okay by _parse_standard_type()

    # TODO test on various different Python versions > 3.8

    # fallback, at the moment we expect this to be called only for type aliases
    # note that in Python 3.12+ there exists typing.TypeAliasType that can be checked with isinstance()
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
    context: Optional[BaseCallerContext] = None

    def __str__(self) -> str:
        base_str = f"{self.name}({', '.join(str(param) for param in self.parameters)})"

        if self.description != "":
            return f"{base_str} - {self.description}"

        return base_str

    def inject_context(self, contexts: Iterable[BaseCallerContext]) -> None:
        """
        Inserts reference to the member of `contexts` of the proper class in self.context.

        Args:
            contexts: An iterable of user-provided context objects.

        Raises:
            SuitableContextNotProvidedError: Ff no element in `contexts` matches `self.context_class`.
        """

        if self.context_class is None:
            return

        try:
            self.context = self.context_class.select_context(contexts)
        except BaseContextError as e:
            raise SuitableContextNotProvidedError(str(self), self.context_class.__name__) from e
