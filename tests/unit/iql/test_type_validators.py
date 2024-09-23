from typing import List, Literal, Union

from typing_extensions import Annotated

from dbally.iql._type_validators import validate_arg_type


def test_literal_validator():
    result = validate_arg_type(Literal["foo", "bar"], "foo")
    assert result.valid is True

    result = validate_arg_type(Literal["foo", "bar"], "foobar")
    assert result.valid is False
    assert result.reason == "foobar must be one of ['foo', 'bar']"


def test_list_validator():
    result = validate_arg_type(List[str], ["foo", "bar"])
    assert result.valid is True

    result = validate_arg_type(list, "wrong")
    assert result.valid is False


def test_annotated_validator():
    result = validate_arg_type(Annotated[str, "This is some value"], "smth")
    assert result.valid is True
    assert result.casted_value == ...
    assert result.reason is None

    result = validate_arg_type(Annotated[str, "This is some value"], 5)
    assert result.valid is False


def test_union_validator():
    result = validate_arg_type(Union[str, int], "smth")
    assert result.valid is True
    assert result.casted_value == ...
    assert result.reason is None

    result = validate_arg_type(Union[str, int], 5)
    assert result.valid is True
    assert result.casted_value == ...
    assert result.reason is None

    result = validate_arg_type(Union[str, int], 5.0)
    assert result.valid is True
    assert result.casted_value == ...
    assert result.reason is None

    result = validate_arg_type(Union[str, int], [1, 2, 3])
    assert result.valid is False
    assert result.casted_value == ...
    assert result.reason == "[1, 2, 3] is not of type <class 'str'>, <class 'int'>"


def test_simple_types():
    assert validate_arg_type(int, 5).valid is True
    assert validate_arg_type(int, "smth").valid is False

    assert validate_arg_type(str, "smth").valid is True
    assert validate_arg_type(str, 5).valid is False

    assert validate_arg_type(bool, True).valid is True
    assert validate_arg_type(bool, [1, 2, 3]).valid is False


def test_type_casts():
    assert validate_arg_type(int, 6.0).valid is True
    assert validate_arg_type(int, 6.7).valid is False
    assert validate_arg_type(float, 5).valid is True
    assert validate_arg_type(bool, 0).valid is True
    assert validate_arg_type(bool, 0).casted_value is False
    assert validate_arg_type(bool, 1).valid is True
    assert validate_arg_type(bool, 1).casted_value is True
