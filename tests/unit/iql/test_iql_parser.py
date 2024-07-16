import re
from typing import List

import pytest

from dbally.iql import IQLArgumentParsingError, IQLQuery, IQLUnsupportedSyntaxError, syntax
from dbally.iql._exceptions import (
    IQLArgumentValidationError,
    IQLEmptyExpressionError,
    IQLFunctionNotExists,
    IQLIncorrectNumberArgumentsError,
    IQLMultipleExpressionsError,
    IQLNoExpressionError,
    IQLSyntaxError,
)
from dbally.iql._processor import IQLProcessor
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping


async def test_iql_parser():
    parsed = await IQLQuery.parse(
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


async def test_iql_parser_arg_error():
    with pytest.raises(IQLArgumentParsingError) as exc_info:
        await IQLQuery.parse(
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


async def test_iql_parser_syntax_error():
    with pytest.raises(IQLSyntaxError) as exc_info:
        await IQLQuery.parse(
            "filter_by_age(",
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

    assert exc_info.match(re.escape("Syntax error in: filter_by_age("))


async def test_iql_parser_multiple_expression_error():
    with pytest.raises(IQLMultipleExpressionsError) as exc_info:
        await IQLQuery.parse(
            "filter_by_age\nfilter_by_age",
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

    assert exc_info.match(re.escape("Multiple expressions or statements in IQL are not supported"))


async def test_iql_parser_empty_expression_error():
    with pytest.raises(IQLEmptyExpressionError) as exc_info:
        await IQLQuery.parse(
            "",
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

    assert exc_info.match(re.escape("Empty IQL expression"))


async def test_iql_parser_no_expression_error():
    with pytest.raises(IQLNoExpressionError) as exc_info:
        await IQLQuery.parse(
            "import filter_by_age",
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

    assert exc_info.match(re.escape("No expression found in IQL: import filter_by_age"))


async def test_iql_parser_unsupported_syntax_error():
    with pytest.raises(IQLUnsupportedSyntaxError) as exc_info:
        await IQLQuery.parse(
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


async def test_iql_parser_method_not_exists():
    with pytest.raises(IQLFunctionNotExists) as exc_info:
        await IQLQuery.parse(
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


async def test_iql_parser_incorrect_number_of_arguments_fail():
    with pytest.raises(IQLIncorrectNumberArgumentsError) as exc_info:
        await IQLQuery.parse(
            "filter_by_age('too old', 40)",
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

    assert exc_info.match(
        re.escape("The method filter_by_age has incorrect number of arguments: filter_by_age('too old', 40)")
    )


async def test_iql_parser_argument_validation_fail():
    with pytest.raises(IQLArgumentValidationError) as exc_info:
        await IQLQuery.parse(
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


def test_keywords_lowercase():
    rv = IQLProcessor._to_lower_except_in_quotes(
        """NOT filter1(230) AND (NOT filter_2("NOT ADMIN") AND filter_('IS NOT ADMIN')) OR NOT filter_4()""",
        keywords=["NOT", "OR", "AND"],
    )
    assert rv == """not filter1(230) and (not filter_2("NOT ADMIN") and filter_('IS NOT ADMIN')) or not filter_4()"""

    rv = IQLProcessor._to_lower_except_in_quotes(
        """NOT NOT NOT 'NOT' "NOT" AND AND "ORNOTAND" """, keywords=["NOT", "OR", "AND"]
    )
    assert rv == """not not not 'NOT' "NOT" and and "ORNOTAND" """
