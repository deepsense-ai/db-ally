from abc import ABC, abstractmethod


class CodeGenerator(ABC):
    """
    An abstract class for code generators.
    """

    @abstractmethod
    def generate(self) -> str:
        """
        Generate the code for the given metadata.

        Returns:
            The generated code.
        """


class Text2SQLViewGenerator(CodeGenerator):
    """
    A code generator for Text2SQL views.
    """

    def generate(self) -> str:
        """
        Generate the code for a Text2SQL view.

        Returns:
            The generated code.
        """
        return "class Text2SQLView:\n    pass"
