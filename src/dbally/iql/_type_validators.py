from dataclasses import dataclass
from typing import _GenericAlias  # type: ignore
from typing import Any, Callable, Dict, Literal, Optional, Type, Union


@dataclass
class _ValidationResult:
    valid: bool
    reason: Optional[str] = None


def _check_literal(required_type: _GenericAlias, value: Any) -> _ValidationResult:
    if value not in required_type.__args__:
        return _ValidationResult(
            False, f"{value} must be one of [{', '.join(repr(x) for x in required_type.__args__)}]"
        )

    return _ValidationResult(True)


TYPE_VALIDATOR: Dict[Any, Callable[[Any, Any], _ValidationResult]] = {Literal: _check_literal}


def validate_arg_type(required_type: Union[Type, _GenericAlias], value: Any) -> _ValidationResult:
    """
    Checks if value is of correct type.

    Args:
        required_type: the type that is required
        value: value to be checked

    Returns:
        _ValidationResult instance
    """
    actual_type = required_type.__origin__ if isinstance(required_type, _GenericAlias) else required_type

    custom_type_checker = TYPE_VALIDATOR.get(actual_type)

    if custom_type_checker:
        return custom_type_checker(required_type, value)

    if isinstance(value, actual_type):
        return _ValidationResult(True)

    return _ValidationResult(False, f"{repr(value)} is not of type {actual_type.__name__}")
