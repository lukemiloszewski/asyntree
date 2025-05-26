import ast
import pathlib
import re
from typing import List, Optional

from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree


def parse_directory(
    directory_path: str = None, include: Optional[List[str]] = None
) -> List[pathlib.Path]:
    path = pathlib.Path(directory_path).resolve() if directory_path else pathlib.Path.cwd()
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    files = [item for item in path.rglob("*") if item.is_file()]

    if include:
        pattern = r"^\.[a-zA-Z]+"
        if not all(re.match(pattern, ext) for ext in include):
            raise ValueError("Extensions must start with '.' followed by alphabetic characters")

        ext_set = {ext.lower() for ext in include}
        files = [f for f in files if f.suffix.lower() in ext_set]

    return files


def walk_directory(directory_path: pathlib.Path, tree: Tree) -> Tree:
    paths = sorted(
        pathlib.Path(directory_path).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )

    for path in paths:
        if path.name.startswith("."):
            continue

        if path.is_dir():
            branch = tree.add(f"{escape(path.name)}")
            walk_directory(path, branch)
        else:
            file_size = path.stat().st_size
            text_filename = Text(path.name, "green")
            text_filename.append(f" ({decimal(file_size)})", "blue")
            tree.add(text_filename)

    return tree


def parse_ast(path: pathlib.Path) -> ast.AST:
    if not path.is_file() or path.suffix != ".py":
        raise ValueError(f"Path must be a Python file: {path}")

    with open(path, "rb") as f:
        rv = ast.parse(f.read(), filename=path)

    return rv
