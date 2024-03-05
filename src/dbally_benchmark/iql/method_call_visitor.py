import ast
from typing import Any, List


class MethodCallVisitor(ast.NodeVisitor):
    """Visitor to extract method calls from an AST."""

    def __init__(self) -> None:
        self._name: List[str] = []

    @property
    def name(self) -> str:
        """Return the method call name."""
        return ".".join(self._name)

    @name.deleter
    def name(self) -> None:
        """Reset the method call name."""
        self._name = []

    def visit_Name(self, node: Any) -> None:  # pylint: disable=invalid-name
        # I had to name this function this way because otherwise
        # it won't work withast.NodeVisitor.
        """
        Updates the method call name after visiting a Name node.

        Args:
            node: The node to visit.
        """

        self._name.insert(0, node.id)

    def visit_Attribute(self, node: Any) -> None:  # pylint: disable=invalid-name
        # I had to name this function this way because otherwise
        # it won't work withast.NodeVisitor.
        """
        Updates the method call name after visiting an Attribute node.

        Args:
            node: The node to visit.
        """

        try:
            self._name.insert(0, node.attr)
        except AttributeError:
            self.generic_visit(node)

    @staticmethod
    def get_method_calls(tree: ast.AST) -> List[str]:
        """
        Return the method calls from the given AST.

        Args:
            tree: The abstract syntax tree to extract method calls from.

        Returns:
            A list of method calls.
        """

        method_calls: List[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                visitor = MethodCallVisitor()
                visitor.visit(node.func)
                method_calls.append(visitor.name)

        return method_calls
