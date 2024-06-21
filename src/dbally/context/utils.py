import typing

from .context import BaseCallerContext


def _extract_filter_context(filter_: typing.Callable) -> typing.Optional[typing.Type[BaseCallerContext]]:
    """
    Extracts a SINGLE caller's context given a StructuredView filter.

    Args:
        filter_: MethodsBaseView filter method (annotated with @decorators.view_filter() decorator)

    Returns:
        A class inheriting from BaseCallerContext. If not context is given among type hints, value None.
    """

    for type_ in typing.get_type_hints(filter_).values():
        if not isinstance(type_, typing.Union) or not hasattr(type_, '__args__'):
            # in the 1st condition here we assume that no user you cannot make filter value context-dependent without providing a base type for it
            # the 2nd condition catches situations when user provides a type hint like typing.Union or typing.Union[int] (single part-clas); in both those cases it should be typing.Union to throw an error, although Python for now accepts this syntax,,,
            continue

        for union_part_type in type_.__args__: # pyright: ignore
            # TODO add custom error for the situation when user provides more than two contexts for a single filter
            # for now we extract only the first context
            if issubclass(union_part_type, BaseCallerContext):
                return union_part_type

    return None
