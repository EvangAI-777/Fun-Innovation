"""Tests for Java code generation utilities."""

from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case, to_camel_case


class TestJavaWriter:
    def test_empty(self):
        w = JavaWriter()
        assert w.build() == ""

    def test_package(self):
        w = JavaWriter()
        w.set_package("com.example.mod")
        result = w.build()
        assert result.startswith("package com.example.mod;\n")

    def test_imports(self):
        w = JavaWriter()
        w.add_import("net.minecraft.block.Block")
        w.add_import("java.util.List")
        result = w.build()
        assert "import java.util.List;" in result
        assert "import net.minecraft.block.Block;" in result
        # java.* should come first
        lines = result.strip().split("\n")
        java_idx = next(i for i, l in enumerate(lines) if "java.util" in l)
        mc_idx = next(i for i, l in enumerate(lines) if "net.minecraft" in l)
        assert java_idx < mc_idx

    def test_no_duplicate_imports(self):
        w = JavaWriter()
        w.add_import("java.util.List", "java.util.List")
        result = w.build()
        assert result.count("java.util.List") == 1

    def test_class_block(self):
        w = JavaWriter()
        w.open_block("public class MyClass")
        w.line("int x = 5;")
        w.close_block()
        result = w.build()
        assert "public class MyClass {" in result
        assert "    int x = 5;" in result
        assert "}" in result

    def test_nested_blocks(self):
        w = JavaWriter()
        w.open_block("public class Outer")
        w.open_block("public void method()")
        w.line("return;")
        w.close_block()
        w.close_block()
        result = w.build()
        assert "        return;" in result

    def test_field(self):
        w = JavaWriter()
        w.field("public static final", "String", "NAME", '"hello"')
        result = w.build()
        assert 'public static final String NAME = "hello";' in result

    def test_annotation(self):
        w = JavaWriter()
        w.annotation("Override")
        w.line("public void run() {}")
        result = w.build()
        assert "@Override" in result

    def test_comment(self):
        w = JavaWriter()
        w.comment("This is a comment")
        assert "// This is a comment" in w.build()

    def test_full_class(self):
        w = JavaWriter()
        w.set_package("com.test")
        w.add_import("java.util.List")
        w.open_block("public class Test")
        w.field("private", "int", "count", "0")
        w.line()
        w.open_block("public int getCount()")
        w.line("return count;")
        w.close_block()
        w.close_block()
        result = w.build()
        assert "package com.test;" in result
        assert "import java.util.List;" in result
        assert "public class Test {" in result
        assert "private int count = 0;" in result
        assert "return count;" in result


class TestHelpers:
    def test_to_java_string(self):
        assert to_java_string("hello") == '"hello"'
        assert to_java_string('say "hi"') == '"say \\"hi\\""'
        assert to_java_string("line\nbreak") == '"line\\nbreak"'

    def test_to_pascal_case(self):
        assert to_pascal_case("cool_mod") == "CoolMod"
        assert to_pascal_case("hello") == "Hello"
        assert to_pascal_case("a_b_c") == "ABC"

    def test_to_camel_case(self):
        assert to_camel_case("cool_mod") == "coolMod"
        assert to_camel_case("hello") == "hello"
        assert to_camel_case("my_great_var") == "myGreatVar"
