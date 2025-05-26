import pathlib
import sys
from typing import Any, Dict, List, Set

from rich.tree import Tree

from asyntree.parser import parse_ast, parse_directory, walk_directory  # noqa: F401
from asyntree.visitor import ImportVisitor, Visitor
from typing import List, Dict
import pathlib
from rich.tree import Tree
from rich.text import Text
from rich.filesize import decimal

def describe(paths: List[pathlib.Path]) -> List[Dict[str, Any]]:
    """Analyze all Python files in a directory and return AST metrics."""
    visitor = Visitor()
    output = []

    for file_path in paths:
        ast_tree = parse_ast(file_path)
        metrics = dict(visitor.run(ast_tree))
        output.append({"path": file_path.name, "ast": metrics})

    return output


def to_tree(paths: List[pathlib.Path]) -> Tree:
    tree = Tree("Directory Structure")
    nodes: Dict[pathlib.Path, Tree] = {}
    
    if not paths:
        return tree
    
    common_parent = paths[0].parent
    for path in paths[1:]:
        while not path.is_relative_to(common_parent):
            common_parent = common_parent.parent
    
    root_name = common_parent.name if common_parent.name else "root"
    root_node = tree.add(Text(root_name, "yellow bold"))
    nodes[common_parent] = root_node
    
    for path in sorted(paths, key=lambda p: p.parts):
        if path.name.startswith("."):
            continue
            
        relative_path = path.relative_to(common_parent)
        current = root_node
        current_parent = common_parent
        
        for part in relative_path.parts[:-1]:
            current_path = current_parent / part
            if current_path not in nodes:
                nodes[current_path] = current.add(Text(part, "yellow bold"))
            current = nodes[current_path]
            current_parent = current_path
        
        file_size = path.stat().st_size
        text_filename = Text(path.name, "green")
        text_filename.append(f" ({decimal(file_size)})", "blue")
        current.add(text_filename)
    
    return tree


def to_llm(paths: List[pathlib.Path], output_file: str = "llm.txt") -> pathlib.Path:
    """Generate (and export) an llm.txt file."""
    content = []

    # directory structure
    content.append("<<<--- Directory Structure --->>>\n")
    tree_lines = to_tree(paths).render().splitlines()
    content.append("\n".join(tree_lines))

    # directory contents
    content.append("<<<--- Directory Contents --->>>\n\n")

    for file_path in paths:
        try:
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()
            content.append(f"<<< {file_path.name} >>>\n")
            content.append(file_content)
            content.append("<<<>>>\n")
        except Exception as e:
            content.append(f"<<< {file_path.name} >>>\n")
            content.append(f"Could not read file: {e}")
            content.append("<<<>>>\n")

    output_path = pathlib.Path(output_file)
    content = "\n".join(content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def to_requirements(
    paths: List[pathlib.Path], output_file: str = "requirements.txt"
) -> pathlib.Path:
    """Generate (and export) a requirements.txt file."""
    imports = _extract_imports(paths)

    external_deps = []
    for dep in sorted(imports):
        if not dep.startswith(".") and dep not in sys.stdlib_module_names:
            root_module = dep.split(".")[0]
            if root_module not in sys.stdlib_module_names:
                external_deps.append(root_module)

    unique_deps = sorted(set(external_deps))

    output_path = pathlib.Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        for dep in unique_deps:
            f.write(f"{dep}\n")

    return output_path


def _extract_imports(paths: List[pathlib.Path]) -> Set[str]:
    """Extract all import dependencies from Python files in a directory."""
    all_imports = set()
    visitor = ImportVisitor()

    for file_path in paths:
        ast_tree = parse_ast(file_path)
        imports = visitor.run(ast_tree)
        all_imports.update(imports)

    return all_imports
