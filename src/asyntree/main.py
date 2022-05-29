import ast

from rich.pretty import pprint
import typer

from asyntree.visitor import Visitor

app = typer.Typer()


@app.command()
def main(path: str = typer.Argument(...)) -> None:
    """Asyntree."""

    with open(path) as source_file:
        source_code = source_file.read()

    tree = ast.parse(source_code)

    visitor = Visitor()
    count = dict(visitor.run(tree))
    sorted_count = sorted(count.items())
    pprint(sorted_count)


if __name__ == "__main__":
    app(prog_name="asyntree")  # pragma: no cover
