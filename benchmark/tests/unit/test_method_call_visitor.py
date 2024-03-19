import ast

import pytest
from dbally_benchmark.iql.method_call_visitor import MethodCallVisitor


@pytest.fixture
def method_call_visitor():
    return MethodCallVisitor()


def test_method_call_visitor(method_call_visitor):
    assert method_call_visitor.get_method_calls(ast.parse("")) == []
    assert method_call_visitor.get_method_calls(ast.parse("filter_by_name('Cody Brown')")) == ["filter_by_name"]
    assert method_call_visitor.get_method_calls(
        ast.parse("taller_than(180) and (older_than(10) or heavier_than(50))")
    ) == ["taller_than", "older_than", "heavier_than"]
