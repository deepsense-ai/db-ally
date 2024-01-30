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

        :arg source: IQL string that needs to be parsed
        :return: IQLQuery object
        """
        return cls(IQLParser(source).parse())
