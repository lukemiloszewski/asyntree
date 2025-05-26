import ast
from collections import Counter
from typing import Set


class Visitor(ast.NodeVisitor):
    """Visitor to count AST node types."""

    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        self.nodes.append(node.__class__.__name__)
        super().generic_visit(node)

    def run(self, code):
        self.nodes.clear()
        self.visit(code)
        return Counter(self.nodes)


class ImportVisitor(ast.NodeVisitor):
    """Visitor to extract import statements and dependencies."""

    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def run(self, tree: ast.AST) -> Set[str]:
        self.imports.clear()
        self.visit(tree)
        return self.imports.copy()
