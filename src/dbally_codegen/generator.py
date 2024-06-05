import inspect
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from textwrap import indent
from types import FunctionType
from typing import Any, List, Optional, Type

from dbally.views.freeform.text2sql import TableConfig
from dbally.views.freeform.text2sql.view import BaseText2SQLView


class CodeGenerator(ABC):
    """
    An abstract class for code generators.
    """

    builtin_module_names = set(sys.builtin_module_names) | {
        "dataclasses",
        "typing",
    }

    def __init__(self, spaces: int = 4) -> None:
        super().__init__()
        self.indentation = spaces * " "
        self.imports = defaultdict(set)
        self.module_imports = set()

    @abstractmethod
    def generate(self) -> str:
        """
        Generate the code for the given metadata.

        Returns:
            The generated code.
        """

    def add_literal_import(self, package: str, name: str) -> None:
        """
        Add a literal import to the generator.

        Args:
            package: The package of the import.
            name: The name of the import.
        """
        # Don't store builtin imports
        if package == "builtins" or not name:
            return
        names = self.imports.setdefault(package, set())
        names.add(name)

    def group_imports(self) -> List[List[str]]:
        """
        Group imports into future, standard library, and third-party imports.

        Returns:
            The grouped imports.
        """
        future_imports = []
        stdlib_imports = []
        thirdparty_imports = []

        for package in sorted(self.imports):
            imports = ", ".join(sorted(self.imports[package]))
            collection = thirdparty_imports
            if package == "__future__":
                collection = future_imports
            elif package in self.builtin_module_names:
                collection = stdlib_imports
            elif package in sys.modules:
                if "site-packages" not in (sys.modules[package].__file__ or ""):
                    collection = stdlib_imports

            collection.append(f"from {package} import {imports}")

        for module in sorted(self.module_imports):
            thirdparty_imports.append(f"import {module}")

        return [group for group in (future_imports, stdlib_imports, thirdparty_imports) if group]

    def render_class_declaration(self, name: str, parents: Optional[List[Type]] = None) -> str:
        """
        Render a class declaration.

        Args:
            name: The name of the class.
            parents: The parent classes of the class.

        Returns:
            The rendered class declaration.
        """
        if parents:
            for parent in parents:
                self.add_literal_import(parent.__module__, parent.__name__)
            parent_names = ", ".join(parent.__name__ for parent in parents)
            return f"class {name}({parent_names}):"
        return f"class {name}:"

    def render_class_method(self, method: FunctionType, body: str = "...") -> str:
        """
        Render a class method.

        Args:
            method: The method to render.
            body: The body of the method.

        Returns:
            The rendered class method.
        """
        method_signature = inspect.signature(method)
        params_annotations = ", ".join(self._parse_param(param) for param in method_signature.parameters.values())
        return_annotation = self._import_annotation(method_signature.return_annotation)
        return f"def {method.__name__}({params_annotations}) -> {return_annotation}:\n{indent(body, self.indentation)}"

    def _parse_param(self, param: inspect.Parameter) -> str:
        """
        Parse the signature of a parameter.

        Args:
            param: The parameter to parse.

        Returns:
            The parsed parameter signature.
        """
        param_signature = param.name
        if param.annotation is not inspect.Parameter.empty:
            param_signature += f": {self._import_annotation(param.annotation)}"
        if param.default is not inspect.Parameter.empty:
            param_signature += f' = "{param.default}"' if isinstance(param.default, str) else f" = {param.default}"
        return param_signature

    def _import_annotation(self, annotation: Type) -> str:
        """
        Recursively import the annotation.

        Args:
            annotation: The annotation to import.

        Returns:
            The imported annotation.
        """
        name = getattr(annotation, "__name__", getattr(annotation, "_name", "Any"))
        if name == "Any":
            annotation = Any

        self.add_literal_import(annotation.__module__, name)

        if getattr(annotation, "__args__", None):
            return f"{name}[{', '.join(self._import_annotation(arg) for arg in annotation.__args__)}]"
        return name


class Text2SQLViewGenerator(CodeGenerator):
    """
    A code generator for Text2SQL views.
    """

    def __init__(self, tables: List[TableConfig], view_name: str = "Text2SQLView") -> None:
        super().__init__()
        self.tables = tables
        self.view_name = view_name

    def generate(self) -> str:
        """
        Generate the code for a Text2SQL view.

        Returns:
            The generated code.
        """
        sections = []

        if view := self.render_view():
            sections.append(view)

        if imports := "\n\n".join("\n".join(line for line in group) for group in self.group_imports()):
            sections.insert(0, imports)

        return "\n\n".join(sections) + "\n"

    def render_view(self) -> str:
        """
        Render the Text2SQL view.

        Returns:
            The rendered Text2SQL view.
        """
        sections = []

        tables = self.render_tables()
        get_tables_method = self.render_class_method(BaseText2SQLView.get_tables, tables)
        sections.append(get_tables_method)

        rendered_sections = "\n\n".join(indent(section, self.indentation) for section in sections)
        declaration = self.render_class_declaration(self.view_name, [BaseText2SQLView])
        return f"{declaration}\n{rendered_sections}"

    def render_tables(self) -> str:
        """
        Render the tables for the Text2SQL view.

        Returns:
            The rendered tables.
        """
        return "return []"
