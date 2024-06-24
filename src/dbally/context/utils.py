import typing

from inspect import isclass

from dbally.context.context import BaseCallerContext
from dbally.views.exposed_functions import MethodParamWithTyping


def _extract_params_and_context(
    filter_method_: typing.Callable, hidden_args: typing.List[str]
) -> typing.Tuple[
    typing.List[MethodParamWithTyping],
    typing.Optional[typing.Type[BaseCallerContext]]
]:
    """
    Processes the MethodsBaseView filter method signauture to extract the args and type hints in the desired format. Context claases are getting excluded the returned MethodParamWithTyping list. Only the first BaseCallerContext class is returned.

    Args:
        filter_method_: MethodsBaseView filter method (annotated with @decorators.view_filter() decorator)

    Returns:
        A tuple. The first field contains the list of arguments, each encapsulated as MethodParamWithTyping. The 2nd is the BaseCallerContext subclass provided for this filter, or None if no context specified.
    """

    params = []
    context = None
    # TODO confirm whether to use typing.get_type_hints(method) or method.__annotations__
    for name_, type_ in typing.get_type_hints(filter_method_).items():
        if name_ in hidden_args:
            continue

        if isclass(type_) and issubclass(type_, BaseCallerContext):
            # this is the case when user provides a context but no other type hint for a specifc arg
            # TODO confirm whether this case should be supported
            context_ = type_
            type_ = typing.Any
        elif typing.get_origin(type_) is typing.Union:
            union_subtypes: typing.List[typing.Type] = []
            for subtype_ in typing.get_args(type_): # type: ignore
                # TODO add custom error for the situation when user provides more than two contexts for a single filter
                # for now we extract only the first context
                if isclass(subtype_) and issubclass(subtype_, BaseCallerContext):
                    if context is None:
                        context = subtype_
                else:
                    union_subtypes.append(subtype_)
            if union_subtypes:
                type_ = typing.Union[tuple(union_subtypes)] # type: ignore
            else:
                type_ = typing.Any  # this ELSE handles the situation when the user provided an typing.Union bare type hint, without specyfing any args. In that case, typing.get_args() returns an empty tuple. Unfortunately, Python does not treat it as an error...

        params.append(MethodParamWithTyping(name_, type_))

    return params, context
