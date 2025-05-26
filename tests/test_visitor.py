import ast
from collections import Counter

from asyntree.visitor import ImportVisitor, Visitor


class TestVisitor:
    def test_visitor_simple_function(self):
        """Test visitor with a simple function."""
        code = "def hello(): return 'world'"
        tree = ast.parse(code)
        visitor = Visitor()

        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert result["Module"] == 1
        assert result["FunctionDef"] == 1
        assert result["Return"] == 1
        assert result["Constant"] == 1

    def test_visitor_complex_code(self):
        """Test visitor with more complex code structures."""
        code = """
class MyClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        if self.value > 0:
            return self.value
        else:
            return 0

def main():
    obj = MyClass(10)
    result = obj.get_value()
    for i in range(5):
        print(i)
"""
        tree = ast.parse(code)
        visitor = Visitor()

        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert result["ClassDef"] == 1
        assert result["FunctionDef"] == 3  # __init__, get_value, main
        assert result["If"] == 1
        assert result["For"] == 1
        assert result["Call"] > 0

    def test_visitor_empty_code(self):
        """Test visitor with empty code."""
        code = ""
        tree = ast.parse(code)
        visitor = Visitor()

        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert result["Module"] == 1
        assert len(result) == 1

    def test_visitor_multiple_runs(self):
        """Test that visitor can be run multiple times and resets correctly."""
        code1 = "def func1(): pass"
        code2 = "def func2(): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        visitor = Visitor()

        result1 = visitor.run(tree1)
        result2 = visitor.run(tree2)

        # Both results should be identical since both codes have same structure
        assert result1 == result2
        assert result1["FunctionDef"] == 1
        assert result2["FunctionDef"] == 1

    def test_visitor_with_imports(self):
        """Test visitor with import statements."""
        code = """
import os
from sys import path
import json as js
"""
        tree = ast.parse(code)
        visitor = Visitor()

        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert result["Import"] == 2  # import os, import json as js
        assert result["ImportFrom"] == 1  # from sys import path
        assert result["alias"] == 3  # os, path, js

    def test_visitor_with_expressions(self):
        """Test visitor with various expressions."""
        code = """
x = 1 + 2 * 3
y = [1, 2, 3]
z = {'a': 1, 'b': 2}
result = x if x > 0 else y[0]
"""
        tree = ast.parse(code)
        visitor = Visitor()

        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert result["BinOp"] == 2  # +, *
        assert result["List"] == 1
        assert result["Dict"] == 1
        assert result["IfExp"] == 1  # Conditional expression

    def test_visitor_nodes_cleared_between_runs(self):
        """Test that visitor internal state is cleared between runs."""
        code = "def test(): pass"
        tree = ast.parse(code)
        visitor = Visitor()

        # First run
        visitor.run(tree)
        first_nodes_count = len(visitor.nodes)

        # Second run
        visitor.run(tree)
        second_nodes_count = len(visitor.nodes)

        # Nodes should be the same count, indicating proper clearing
        assert first_nodes_count == second_nodes_count


class TestImportVisitor:
    def test_import_visitor_simple_imports(self):
        """Test ImportVisitor with simple import statements."""
        code = """
import os
import sys
import json
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert "os" in result
        assert "sys" in result
        assert "json" in result
        assert len(result) == 3

    def test_import_visitor_from_imports(self):
        """Test ImportVisitor with from imports."""
        code = """
from pathlib import Path
from collections import Counter
from typing import List, Dict
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert "pathlib" in result
        assert "collections" in result
        assert "typing" in result
        assert len(result) == 3

    def test_import_visitor_mixed_imports(self):
        """Test ImportVisitor with mixed import types."""
        code = """
import os
import sys
from pathlib import Path
from collections import Counter, defaultdict
import json as js
from typing import List
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        expected = {"os", "sys", "pathlib", "collections", "json", "typing"}
        assert result == expected

    def test_import_visitor_aliased_imports(self):
        """Test ImportVisitor with aliased imports."""
        code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert "numpy" in result
        assert "pandas" in result
        assert "matplotlib" in result
        # Aliases should not be in the result, only module names
        assert "np" not in result
        assert "pd" not in result
        assert "plt" not in result

    def test_import_visitor_submodule_imports(self):
        """Test ImportVisitor with submodule imports."""
        code = """
import xml.etree.ElementTree
from urllib.request import urlopen
from email.mime.text import MIMEText
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert "xml.etree.ElementTree" in result
        assert "urllib.request" in result
        assert "email.mime.text" in result

    def test_import_visitor_relative_imports(self):
        """Test ImportVisitor with relative imports."""
        code = """
from . import module1
from ..parent import module2
from .sibling import function
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        # Note: relative imports have module=None in some cases
        # The visitor should handle this gracefully

    def test_import_visitor_empty_code(self):
        """Test ImportVisitor with code containing no imports."""
        code = """
def hello():
    return "world"

class MyClass:
    pass
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert len(result) == 0

    def test_import_visitor_multiple_runs(self):
        """Test that ImportVisitor can be run multiple times and resets correctly."""
        code1 = "import os"
        code2 = "import sys"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        visitor = ImportVisitor()

        result1 = visitor.run(tree1)
        result2 = visitor.run(tree2)

        assert result1 == {"os"}
        assert result2 == {"sys"}
        # Each run should only contain its own imports

    def test_import_visitor_star_imports(self):
        """Test ImportVisitor with star imports."""
        code = """
from os import *
from sys import *
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert "os" in result
        assert "sys" in result

    def test_import_visitor_imports_cleared_between_runs(self):
        """Test that ImportVisitor internal state is cleared between runs."""
        code = "import os"
        tree = ast.parse(code)
        visitor = ImportVisitor()

        # First run
        result1 = visitor.run(tree)
        first_imports_count = len(visitor.imports)

        # Second run with different code
        code2 = "import sys"
        tree2 = ast.parse(code2)
        result2 = visitor.run(tree2)
        second_imports_count = len(visitor.imports)

        # Internal state should be cleared, only containing current run's imports
        assert result1 == {"os"}
        assert result2 == {"sys"}
        assert first_imports_count == 1
        assert second_imports_count == 1

    def test_import_visitor_from_import_with_none_module(self):
        """Test ImportVisitor handles from imports with None module gracefully."""
        # This can happen with certain types of relative imports
        visitor = ImportVisitor()

        # Create a mock ImportFrom node with module=None
        import_node = ast.ImportFrom(
            module=None, names=[ast.alias(name="something", asname=None)], level=1
        )

        # This should not crash
        visitor.visit_ImportFrom(import_node)

        # The module should not be added since it's None
        assert None not in visitor.imports
