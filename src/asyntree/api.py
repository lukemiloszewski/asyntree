import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

from asyntree.parser import parse_path, parse_tree
from asyntree.visitor import ImportVisitor, Visitor


def process_ast(tree: ast.AST, visitor: Visitor) -> Dict[str, int]:
    """Process an AST with a given visitor and return the results."""
    rv = dict(visitor.run(tree))
    return rv


def analyze_directory(path: str) -> List[Dict[str, Any]]:
    """Analyze all Python files in a directory and return AST metrics."""
    paths = parse_path(path)
    output = []
    visitor = Visitor()

    for p in paths:
        tree = parse_tree(p)
        metrics = process_ast(tree, visitor)
        output.append({"path": p.name, "ast": metrics})

    return output


def generate_tree_structure(path: str, prefix: str = "", is_last: bool = True) -> List[str]:
    """Generate a tree structure representation of a directory."""
    path_obj = Path(path).resolve()
    tree_lines = []

    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    def _build_tree(current_path: Path, current_prefix: str = "", is_root: bool = True):
        if is_root:
            tree_lines.append(f"{current_path.name}/")
            items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        else:
            items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1

            if is_root:
                connector = "└── " if is_last_item else "├── "
                new_prefix = "    " if is_last_item else "│   "
            else:
                connector = current_prefix + ("└── " if is_last_item else "├── ")
                new_prefix = current_prefix + ("    " if is_last_item else "│   ")

            if item.is_dir():
                tree_lines.append(f"{connector}{item.name}/")
                _build_tree(item, new_prefix, False)
            else:
                tree_lines.append(f"{connector}{item.name}")

    if path_obj.is_file():
        tree_lines.append(path_obj.name)
    else:
        _build_tree(path_obj)

    return tree_lines


def export_directory_contents(path: str, output_file: str = "llm.txt") -> str:
    """Export directory contents to a markdown file suitable for LLMs."""
    path_obj = Path(path).resolve()

    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    content = []
    content.append(f"# Directory Export: {path_obj.name}\n")

    content.append("## Directory Structure\n")
    content.append("```")
    tree_lines = generate_tree_structure(str(path_obj))
    content.extend(tree_lines)
    content.append("```\n")

    content.append("## File Contents\n")

    def _process_directory(dir_path: Path, relative_base: Path):
        for item in sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if item.is_file():
                relative_path = item.relative_to(relative_base)
                try:
                    with open(item, encoding="utf-8") as f:
                        file_content = f.read()

                    content.append(f"### `{relative_path}`\n")

                    suffix = item.suffix.lower()
                    if suffix == ".py":
                        lang = "python"
                    elif suffix in [".md", ".markdown"]:
                        lang = "markdown"
                    elif suffix in [".yml", ".yaml"]:
                        lang = "yaml"
                    elif suffix in [".json"]:
                        lang = "json"
                    elif suffix in [".toml"]:
                        lang = "toml"
                    elif suffix in [".txt", ".rst"]:
                        lang = "text"
                    else:
                        lang = ""

                    content.append(f"```{lang}")
                    content.append(file_content)
                    content.append("```\n")

                except (UnicodeDecodeError, PermissionError) as e:
                    content.append(f"### `{relative_path}`\n")
                    content.append(f"*Could not read file: {e}*\n")

            elif item.is_dir() and not item.name.startswith("."):
                _process_directory(item, relative_base)

    if path_obj.is_file():
        try:
            with open(path_obj, encoding="utf-8") as f:
                file_content = f.read()
            content.append(f"### `{path_obj.name}`\n")
            content.append("```")
            content.append(file_content)
            content.append("```\n")
        except (UnicodeDecodeError, PermissionError) as e:
            content.append(f"*Could not read file: {e}*\n")
    else:
        _process_directory(path_obj, path_obj)

    output_path = Path(output_file)
    final_content = "\n".join(content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    return str(output_path.resolve())


def extract_dependencies(path: str) -> Set[str]:
    """Extract all import dependencies from Python files in a directory."""
    paths = parse_path(path)
    all_imports = set()
    visitor = ImportVisitor()

    for p in paths:
        tree = parse_tree(p)
        imports = visitor.run(tree)
        all_imports.update(imports)

    return all_imports


def generate_requirements_txt(path: str, output_file: str = "requirements.txt") -> str:
    """Generate a requirements.txt file from imports found in Python files."""
    dependencies = extract_dependencies(path)

    external_deps = []

    for dep in sorted(dependencies):
        if not dep.startswith(".") and dep not in sys.stdlib_module_names:
            root_module = dep.split(".")[0]
            if root_module not in sys.stdlib_module_names:
                external_deps.append(root_module)

    unique_deps = sorted(set(external_deps))

    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Generated requirements.txt\n")
        f.write("# Note: You may need to specify versions manually\n")
        f.write("\n")
        for dep in unique_deps:
            f.write(f"{dep}\n")

    return str(output_path.resolve())
