import sys

import typer
from rich.pretty import pprint

from asyntree.api import process_ast
from asyntree.parser import parse_path, parse_tree
from asyntree.visitor import Visitor

app = typer.Typer(add_completion=False)


@app.command()
def main(
    path: str = typer.Argument(..., help="Input a directory or file path"),
) -> None:
    paths = parse_path(path)

    output = []
    visitor = Visitor()

    for p in paths:
        tree = parse_tree(p)
        metrics = process_ast(tree, visitor)
        output.append({"path": p.name, "ast": metrics})

    pprint(output, max_length=50)

    sys.stdout.flush()
    sys.stderr.flush()
