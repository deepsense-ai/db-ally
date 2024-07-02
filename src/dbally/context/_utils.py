import typing_extensions as type_ext

from typing import Sequence, Tuple, Optional, Type, Any, Union
from inspect import isclass

from dbally.context.context import BaseCallerContext
from dbally.views.exposed_functions import MethodParamWithTyping


def _extract_params_and_context(
    filter_method_: type_ext.Callable, hidden_args: Sequence[str]
) -> Tuple[Sequence[MethodParamWithTyping], Optional[Type[BaseCallerContext]]]:
    """
    Processes the MethodsBaseView filter method signauture to extract the args and type hints in the desired format.
    Context claases are getting excluded the returned MethodParamWithTyping list. Only the first BaseCallerContext
    class is returned.

    Args:
        filter_method_: MethodsBaseView filter method (annotated with @decorators.view_filter() decorator)

    Returns:
        A tuple. The first field contains the list of arguments, each encapsulated as MethodParamWithTyping.
        The 2nd is the BaseCallerContext subclass provided for this filter, or None if no context specified.
    """

    params = []
    context = None
    # TODO confirm whether to use typing.get_type_hints(method) or method.__annotations__
    for name_, type_ in type_ext.get_type_hints(filter_method_).items():
        if name_ in hidden_args:
            continue

        if isclass(type_) and issubclass(type_, BaseCallerContext):
            # this is the case when user provides a context but no other type hint for a specifc arg
            context = type_
            type_ = Any
        elif type_ext.get_origin(type_) is Union:
            union_subtypes = type_ext.get_args(type_)
            if not union_subtypes:
                type_ = Any

            for subtype_ in union_subtypes:  # type: ignore
                # TODO add custom error for the situation when user provides more than two contexts for a single filter
                # for now we extract only the first context
                if isclass(subtype_) and issubclass(subtype_, BaseCallerContext):
                    if context is None:
                        context = subtype_

        params.append(MethodParamWithTyping(name_, type_))

    return params, context


def _does_arg_allow_context(arg: MethodParamWithTyping) -> bool:
    if type_ext.get_origin(arg.type) is not Union and not issubclass(arg.type, BaseCallerContext):
        return False

    for subtype in type_ext.get_args(arg.type):
        if issubclass(subtype, BaseCallerContext):
            return True

    return False
