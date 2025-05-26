import ast
from collections import Counter

from asyntree.visitor import ImportVisitor, Visitor


class TestVisitor:
    def test_visitor_empty_code(self):
        code = ""
        tree = ast.parse(code)
        visitor = Visitor()
        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert len(result) == 1
        assert result["Module"] == 1

    def test_visitor_complex_code(self):
        code = """
import os
from sys import path
import json as js

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

    x = 1 + 2 * 3
    y = [1, 2, 3]
    z = {'a': 1, 'b': 2}
    final = x if x > 0 else y[0]
"""
        tree = ast.parse(code)
        visitor = Visitor()
        result = visitor.run(tree)

        assert isinstance(result, Counter)
        assert len(result) == 28
        assert result["Module"] == 1
        assert result["Import"] == 2
        assert result["alias"] == 3
        assert result["ImportFrom"] == 1
        assert result["ClassDef"] == 1
        assert result["FunctionDef"] == 3
        assert result["arguments"] == 3
        assert result["arg"] == 3
        assert result["Assign"] == 7
        assert result["Attribute"] == 4
        assert result["Name"] == 19
        assert result["Load"] == 17
        assert result["Store"] == 8
        assert result["If"] == 1
        assert result["Compare"] == 2
        assert result["Gt"] == 2
        assert result["Constant"] == 16
        assert result["Return"] == 2
        assert result["Call"] == 4
        assert result["For"] == 1
        assert result["Expr"] == 1
        assert result["BinOp"] == 2
        assert result["Add"] == 1
        assert result["Mult"] == 1
        assert result["List"] == 1
        assert result["Dict"] == 1
        assert result["IfExp"] == 1
        assert result["Subscript"] == 1


class TestImportVisitor:
    def test_import_visitor_simple_imports(self):
        code = """
import os
import sys
import json
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert result == {"os", "sys", "json"}

    def test_import_visitor_from_imports(self):
        code = """
from pathlib import Path
from collections import Counter
from typing import List, Dict
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert result == {"pathlib", "collections", "typing"}

    def test_import_visitor_mixed_imports(self):
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
        assert result == {"os", "sys", "pathlib", "collections", "json", "typing"}

    def test_import_visitor_aliased_imports(self):
        code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert result == {"numpy", "pandas", "matplotlib"}

    def test_import_visitor_submodule_imports(self):
        code = """
import xml.etree.ElementTree
from urllib.request import urlopen
from email.mime.text import MIMEText
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert result == {"xml", "urllib", "email"}

    def test_import_visitor_relative_imports(self):
        code = """
from . import module1
from ..parent import module2
from .sibling import function
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()

        result = visitor.run(tree)

        assert isinstance(result, set)
        assert len(result) == 0

    def test_import_visitor_star_imports(self):
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

    def test_import_visitor_empty_code(self):
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
        code1 = "import os"
        code2 = "import sys"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        visitor = ImportVisitor()

        result1 = visitor.run(tree1)
        result2 = visitor.run(tree2)

        assert result1 == {"os"}
        assert result2 == {"sys"}
