
from ._parser import IQLParser
from ._syntax import IQL


class IQLQuery:
    """
    IQLQuery container. It stores IQL as a syntax tree defined in `IQL` class.
    """

    root: IQL.Node

    def __init__(self, root: IQL.Node):
        self.root = root

    @classmethod
    def parse(cls, source: str) -> 'IQLQuery':
        """
        Parse IQL string to IQLQuery object.

        :arg source: IQL string that needs to be parsed
        :return: IQLQuery object
        """
        return cls(IQLParser(source).parse())
