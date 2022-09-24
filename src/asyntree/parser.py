import ast
import sys
from pathlib import Path
from typing import List


def parse_path(raw_path) -> List[Path]:
    paths = []

    path = Path(raw_path).resolve()
    if path.is_dir():
        paths.extend(path.rglob("*.py"))
    elif path.exists():
        paths.append(path)
    else:
        sys.exit(f"No such file or directory: {path}")

    return paths


def parse_tree(path: Path) -> ast.AST:
    with open(path, "rb") as f:
        return ast.parse(f.read(), filename=path)
