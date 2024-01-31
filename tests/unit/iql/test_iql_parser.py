import re

import pytest

from dbally.iql import IQLArgumentParsingError, IQLQuery, IQLUnsupportedSyntaxError, syntax


def test_iql_parser():
    parsed = IQLQuery.parse(
        "not (filter_by_name(['John', 'Anne']) and filter_by_city('cracow') and filter_by_company('deepsense.ai'))"
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
        IQLQuery.parse("filter_by_city('Cracow') and filter_by_name(lambda x: x + 1)")

    assert exc_info.match(re.escape("Not a valid IQL argument: lambda x: x + 1"))


def test_iql_parser_unsupported_syntax_error():
    with pytest.raises(IQLUnsupportedSyntaxError) as exc_info:
        IQLQuery.parse("filter_by_age() >= 30")

    assert exc_info.match(re.escape("Compare syntax is not supported in IQL: filter_by_age() >= 30"))
