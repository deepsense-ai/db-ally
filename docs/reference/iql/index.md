# Syntax

This reference page describes all building blocks of the [Intermediate Query Language (IQL)](../../concepts/iql.md).


::: dbally.iql.syntax.Node


::: dbally.iql.syntax.FunctionCall
    options:
        members:
        - name
        - arguments

::: dbally.iql.syntax.BoolOp
    options:
        members:
        - match

::: dbally.iql.syntax.And
    options:
        members:
        - children

::: dbally.iql.syntax.Or
    options:
        members:
        - children

::: dbally.iql.syntax.Not
    options:
        members:
        - child