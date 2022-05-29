import ast
from collections import Counter


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = list()

    def generic_visit(self, node):
        self.nodes.append(node.__class__.__name__)
        super().generic_visit(node)

    def run(self, code):
        self.visit(code)
        return Counter(self.nodes)
