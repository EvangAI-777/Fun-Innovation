"""Java source code generation utilities."""

from __future__ import annotations

from io import StringIO


class JavaWriter:
    """Builds a Java source file with proper formatting."""

    def __init__(self) -> None:
        self._package: str = ""
        self._imports: list[str] = []
        self._body = StringIO()
        self._indent: int = 0

    def set_package(self, package: str) -> JavaWriter:
        self._package = package
        return self

    def add_import(self, *imports: str) -> JavaWriter:
        for imp in imports:
            if imp not in self._imports:
                self._imports.append(imp)
        return self

    def line(self, text: str = "") -> JavaWriter:
        if text:
            self._body.write("    " * self._indent + text + "\n")
        else:
            self._body.write("\n")
        return self

    def open_block(self, header: str) -> JavaWriter:
        self.line(f"{header} {{")
        self._indent += 1
        return self

    def close_block(self) -> JavaWriter:
        self._indent = max(0, self._indent - 1)
        self.line("}")
        return self

    def annotation(self, name: str) -> JavaWriter:
        return self.line(f"@{name}")

    def field(self, modifiers: str, type_name: str, name: str, value: str | None = None) -> JavaWriter:
        if value is not None:
            return self.line(f"{modifiers} {type_name} {name} = {value};")
        return self.line(f"{modifiers} {type_name} {name};")

    def comment(self, text: str) -> JavaWriter:
        return self.line(f"// {text}")

    def build(self) -> str:
        out = StringIO()
        if self._package:
            out.write(f"package {self._package};\n\n")
        if self._imports:
            # Group imports: java.*, then others
            java_imports = sorted(i for i in self._imports if i.startswith("java."))
            other_imports = sorted(i for i in self._imports if not i.startswith("java."))
            for imp in java_imports:
                out.write(f"import {imp};\n")
            if java_imports and other_imports:
                out.write("\n")
            for imp in other_imports:
                out.write(f"import {imp};\n")
            out.write("\n")
        out.write(self._body.getvalue())
        return out.getvalue()


def to_java_string(value: str) -> str:
    """Wrap a Python string as a Java string literal."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def to_pascal_case(snake: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in snake.split("_"))


def to_camel_case(snake: str) -> str:
    """Convert snake_case to camelCase."""
    parts = snake.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])
