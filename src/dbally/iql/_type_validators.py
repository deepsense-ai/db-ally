from dataclasses import dataclass
from typing import (  # type: ignore
    Annotated,
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    Type,
    Union,
    _GenericAlias,
    get_args,
    get_origin,
)


@dataclass
class _ValidationResult:
    valid: bool
    casted_value: Any = ...
    reason: Optional[str] = None


def _check_annotated(required_type: Annotated, value: Any) -> _ValidationResult:
    type_args = get_args(required_type)
    return validate_arg_type(type_args[0], value)


def _check_literal(required_type: _GenericAlias, value: Any) -> _ValidationResult:
    type_args = get_args(required_type)
    if value not in type_args:
        return _ValidationResult(False, reason=f"{value} must be one of [{', '.join(repr(x) for x in type_args)}]")

    return _ValidationResult(True)


def _check_union(required_type: _GenericAlias, value: Any) -> _ValidationResult:
    type_args = get_args(required_type)

    for subtype in get_args(required_type):
        res = validate_arg_type(subtype, value)
        if res.valid:
            return _ValidationResult(True)

    return _ValidationResult(False, reason=f"{repr(value)} is not of type {', '.join(repr(x) for x in type_args)}")


def _check_float(required_type: Type[float], value: Any) -> _ValidationResult:
    if isinstance(value, float):
        return _ValidationResult(True)
    if isinstance(value, int):
        return _ValidationResult(True, casted_value=float(value))

    return _ValidationResult(False, reason=f"{repr(value)} is not of type {required_type.__name__}")


def _check_int(required_type: Type[int], value: Any) -> _ValidationResult:
    if isinstance(value, int):
        return _ValidationResult(True)
    if isinstance(value, float) and value.is_integer():
        return _ValidationResult(True, casted_value=int(value))

    return _ValidationResult(False, reason=f"{repr(value)} is not of type {required_type.__name__}")


def _check_bool(required_type: Type[bool], value: Any) -> _ValidationResult:
    if isinstance(value, bool):
        return _ValidationResult(True)
    if isinstance(value, int) and (value in (0, 1)):
        return _ValidationResult(True, casted_value=bool(value))

    return _ValidationResult(False, reason=f"{repr(value)} is not of type {required_type.__name__}")


TYPE_VALIDATOR: Dict[Any, Callable[[Any, Any], _ValidationResult]] = {
    Annotated: _check_annotated,
    Literal: _check_literal,
    Union: _check_union,
    float: _check_float,
    int: _check_int,
    bool: _check_bool,
}


def validate_arg_type(required_type: Union[Type, _GenericAlias], value: Any) -> _ValidationResult:
    """
    Checks if value is of correct type.

    Args:
        required_type: the type that is required
        value: value to be checked

    Returns:
        _ValidationResult instance
    """
    actual_type = get_origin(required_type) or required_type

    if custom_type_checker := TYPE_VALIDATOR.get(actual_type):
        return custom_type_checker(required_type, value)

    if isinstance(value, actual_type):
        return _ValidationResult(True)

    return _ValidationResult(False, f"{repr(value)} is not of type {actual_type.__name__}")
