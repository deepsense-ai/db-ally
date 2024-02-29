import re
from typing import List

import pytest

from dbally.iql import IQLArgumentParsingError, IQLQuery, IQLUnsupportedSyntaxError, syntax
from dbally.iql._exceptions import IQLArgumentValidationError, IQLFunctionNotExists
from dbally.views.base import ExposedFunction, MethodParamWithTyping


def test_iql_parser():
    parsed = IQLQuery.parse(
        "not (filter_by_name(['John', 'Anne']) and filter_by_city('cracow') and filter_by_company('deepsense.ai'))",
        allowed_functions=[
            ExposedFunction(
                name="filter_by_name", description="", parameters=[MethodParamWithTyping(name="name", type=List[str])]
            ),
            ExposedFunction(
                name="filter_by_city", description="", parameters=[MethodParamWithTyping(name="city", type=str)]
            ),
            ExposedFunction(
                name="filter_by_company", description="", parameters=[MethodParamWithTyping(name="company", type=str)]
            ),
        ],
    )

    not_op = parsed.root
    assert isinstance(not_op, syntax.Not)

    and_op = not_op.child
    assert isinstance(and_op, syntax.And)

    name_filter, city_filter, company_filter = and_op.children

    assert isinstance(name_filter, syntax.FunctionCall)
    assert name_filter.arguments[0] == ["John", "Anne"]

    assert isinstance(city_filter, syntax.FunctionCall)
    assert city_filter.arguments[0] == "cracow"

    assert isinstance(company_filter, syntax.FunctionCall)
    assert company_filter.arguments[0] == "deepsense.ai"


def test_iql_parser_arg_error():
    with pytest.raises(IQLArgumentParsingError) as exc_info:
        IQLQuery.parse(
            "filter_by_city('Cracow') and filter_by_name(lambda x: x + 1)",
            allowed_functions=[
                ExposedFunction(
                    name="filter_by_city",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="city", type=str),
                    ],
                ),
                ExposedFunction(
                    name="filter_by_name",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="name", type=str),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("Not a valid IQL argument: lambda x: x + 1"))


def test_iql_parser_unsupported_syntax_error():
    with pytest.raises(IQLUnsupportedSyntaxError) as exc_info:
        IQLQuery.parse(
            "filter_by_age() >= 30",
            allowed_functions=[
                ExposedFunction(
                    name="filter_by_age",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="age", type=int),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("Compare syntax is not supported in IQL: filter_by_age() >= 30"))


def test_iql_parser_method_not_exists():
    with pytest.raises(IQLFunctionNotExists) as exc_info:
        IQLQuery.parse(
            "filter_by_how_old_somebody_is(40)",
            allowed_functions=[
                ExposedFunction(
                    name="filter_by_age",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="age", type=int),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("Function filter_by_how_old_somebody_is not exists: filter_by_how_old_somebody_is"))


def test_iql_parser_argument_validation_fail():
    with pytest.raises(IQLArgumentValidationError) as exc_info:
        IQLQuery.parse(
            "filter_by_age('too old')",
            allowed_functions=[
                ExposedFunction(
                    name="filter_by_age",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="age", type=int),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("'too old' is not of type int: 'too old'"))
