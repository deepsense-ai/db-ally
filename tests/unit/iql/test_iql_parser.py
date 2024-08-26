import re
from typing import List

import pytest

from dbally.iql import IQLArgumentParsingError, IQLUnsupportedSyntaxError, syntax
from dbally.iql._exceptions import (
    IQLArgumentValidationError,
    IQLFunctionNotExists,
    IQLIncorrectNumberArgumentsError,
    IQLMultipleStatementsError,
    IQLNoExpressionError,
    IQLNoStatementError,
    IQLSyntaxError,
)
from dbally.iql._processor import IQLProcessor
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.views.exposed_functions import ExposedFunction, MethodParamWithTyping


async def test_iql_filter_parser():
    parsed = await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_arg_error():
    with pytest.raises(IQLArgumentParsingError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_syntax_error():
    with pytest.raises(IQLSyntaxError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_multiple_expression_error():
    with pytest.raises(IQLMultipleStatementsError) as exc_info:
        await IQLFiltersQuery.parse(
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

    assert exc_info.match(re.escape("Multiple statements in IQL are not supported"))


async def test_iql_filter_parser_empty_expression_error():
    with pytest.raises(IQLNoStatementError) as exc_info:
        await IQLFiltersQuery.parse(
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

    assert exc_info.match(re.escape("Empty IQL"))


async def test_iql_filter_parser_no_expression_error():
    with pytest.raises(IQLNoExpressionError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_unsupported_syntax_error():
    with pytest.raises(IQLUnsupportedSyntaxError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_method_not_exists():
    with pytest.raises(IQLFunctionNotExists) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_incorrect_number_of_arguments_fail():
    with pytest.raises(IQLIncorrectNumberArgumentsError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_filter_parser_argument_validation_fail():
    with pytest.raises(IQLArgumentValidationError) as exc_info:
        await IQLFiltersQuery.parse(
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


async def test_iql_aggregation_parser():
    parsed = await IQLAggregationQuery.parse(
        "mean_age_by_city('Paris')",
        allowed_functions=[
            ExposedFunction(
                name="mean_age_by_city",
                description="",
                parameters=[
                    MethodParamWithTyping(name="city", type=str),
                ],
            ),
        ],
    )

    assert isinstance(parsed.root, syntax.FunctionCall)
    assert parsed.root.name == "mean_age_by_city"
    assert parsed.root.arguments == ["Paris"]


async def test_iql_aggregation_parser_arg_error():
    with pytest.raises(IQLArgumentParsingError) as exc_info:
        await IQLAggregationQuery.parse(
            "mean_age_by_city(lambda x: x + 1)",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="city", type=str),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("Not a valid IQL argument: lambda x: x + 1"))


async def test_iql_aggregation_parser_syntax_error():
    with pytest.raises(IQLSyntaxError) as exc_info:
        await IQLAggregationQuery.parse(
            "mean_age_by_city(",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="city", type=str),
                    ],
                ),
            ],
        )

    assert exc_info.match(re.escape("Syntax error in: mean_age_by_city("))


async def test_iql_aggregation_parser_multiple_expression_error():
    with pytest.raises(IQLMultipleStatementsError) as exc_info:
        await IQLAggregationQuery.parse(
            "mean_age_by_city\nmean_age_by_city",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )

    assert exc_info.match(re.escape("Multiple statements in IQL are not supported"))


async def test_iql_aggregation_parser_empty_expression_error():
    with pytest.raises(IQLNoStatementError) as exc_info:
        await IQLAggregationQuery.parse(
            "",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )

    assert exc_info.match(re.escape("Empty IQL"))


async def test_iql_aggregation_parser_no_expression_error():
    with pytest.raises(IQLNoExpressionError) as exc_info:
        await IQLAggregationQuery.parse(
            "import mean_age_by_city",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )

    assert exc_info.match(re.escape("No expression found in IQL: import mean_age_by_city"))


@pytest.mark.parametrize(
    "iql, info",
    [
        ("mean_age_by_city() >= 30", "Compare syntax is not supported in IQL: mean_age_by_city() >= 30"),
        (
            "mean_age_by_city('Paris') and mean_age_by_city('London')",
            "BoolOp syntax is not supported in IQL: mean_age_by_city('Paris') and mean_age_by_city('London')",
        ),
        (
            "mean_age_by_city('Paris') or mean_age_by_city('London')",
            "BoolOp syntax is not supported in IQL: mean_age_by_city('Paris') or mean_age_by_city('London')",
        ),
        ("not mean_age_by_city('Paris')", "UnaryOp syntax is not supported in IQL: not mean_age_by_city('Paris')"),
    ],
)
async def test_iql_aggregation_parser_unsupported_syntax_error(iql, info):
    with pytest.raises(IQLUnsupportedSyntaxError) as exc_info:
        await IQLAggregationQuery.parse(
            iql,
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )
    assert exc_info.match(re.escape(info))


async def test_iql_aggregation_parser_method_not_exists():
    with pytest.raises(IQLFunctionNotExists) as exc_info:
        await IQLAggregationQuery.parse(
            "mean_age_by_town()",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )

    assert exc_info.match(re.escape("Function mean_age_by_town not exists: mean_age_by_town"))


async def test_iql_aggregation_parser_incorrect_number_of_arguments_fail():
    with pytest.raises(IQLIncorrectNumberArgumentsError) as exc_info:
        await IQLAggregationQuery.parse(
            "mean_age_by_city('too old')",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[],
                ),
            ],
        )

    assert exc_info.match(
        re.escape("The method mean_age_by_city has incorrect number of arguments: mean_age_by_city('too old')")
    )


async def test_iql_aggregation_parser_argument_validation_fail():
    with pytest.raises(IQLArgumentValidationError):
        await IQLAggregationQuery.parse(
            "mean_age_by_city(12)",
            allowed_functions=[
                ExposedFunction(
                    name="mean_age_by_city",
                    description="",
                    parameters=[
                        MethodParamWithTyping(name="city", type=str),
                    ],
                ),
            ],
        )


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
