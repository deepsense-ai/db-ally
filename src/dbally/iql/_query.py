from typing import Iterator, List

from . import syntax
from ._parser import IQLParser


class IQLQuery:
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: syntax.Node

    def __init__(self, root: syntax.Node):
        self.root = root

    @classmethod
    def parse(cls, source: str) -> "IQLQuery":
        """
        Parse IQL string to IQLQuery object.

        :param source: IQL string that needs to be parsed
        :return: IQLQuery object
        """
        return cls(IQLParser(source).parse())


class IQLActions:
    """
    IQLActions container. It stores list of function calls to apply in order.
    """

    actions: List[syntax.FunctionCall]

    def __init__(self, actions: List[syntax.FunctionCall]):
        self.actions = actions

    @classmethod
    def parse(cls, source: str) -> "IQLActions":
        """
        Parse IQL action string to IQLActions object.

        :param source: IQL string that needs to be parsed
        :return: IQLActions object
        """
        return cls(IQLParser(source).parse_actions())

    def __iter__(self) -> Iterator[syntax.FunctionCall]:
        yield from self.actions
