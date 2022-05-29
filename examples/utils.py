import ast
import inspect


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = list()

    def generic_visit(self, node):
        self.nodes.append(node.__class__.__name__)
        super().generic_visit(node)

    def get_counter(self):
        return Counter(self.nodes)


class Visitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print(f'entering {node.__class__.__name__}')  # pre-order
        super().generic_visit(node)
        print(f'leaving {node.__class__.__name__}')  # post-order

    def display_code(self, node):
        print(f'entering {ast.dump(node)}')
        super().generic_visit(node)

    def visit_Module(self, node):
        self.names = set()
        self.generic_visit(node)
        print(self.names)

    def visit_Name(self, node):
        self.names.add(node.id)

    def visit_Await(self, node):
        print('Node type: Await\nFields: ', node._fields)
        self.generic_visit(node)

    def visit_Call(self,node):
        print('Node type: Call\nFields: ', node._fields)
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self,node):
        print('Node type: Name\nFields: ', node._fields)
        ast.NodeVisitor.generic_visit(self, node)


def get_ast(code):
    return ast.dump(ast.parse(code), indent=2)


def get_source(code):
    return inspect.getsource(code)


# --- EXAMPLES ---


visitor = Visitor()

tree = ast.parse('''
age = 21
print(age)
''')
visitor.visit(tree)

from collections import Counter

counter = Counter()

for x in range(10):
    counter.update([x])


Counter(z)
