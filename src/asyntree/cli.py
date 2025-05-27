import pathlib
from typing import Annotated, List, Optional

import typer
from rich.console import Console

from asyntree.api import (
    describe,
    to_llm,
    to_requirements,
    to_tree,
)
from asyntree.parser import parse_directory

app = typer.Typer(add_completion=False)
console = Console()


@app.command("describe")
def cli_describe(
    path: Optional[str] = typer.Argument(None, help="Input a directory path"),
) -> None:
    """Describe the ast nodes of all python files."""
    try:
        file_paths = parse_directory(path, include=[".py"])
        cli_output = describe(file_paths)
        console.print(cli_output)
    except Exception as e:
        console.print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-tree")
def cli_to_tree(
    path: Annotated[Optional[str], typer.Argument(help="Input a directory path")] = None,
    include: Annotated[
        Optional[List[str]], typer.Option("--include", "-i", help="File extensions to include")
    ] = None,
    exclude: Annotated[
        Optional[List[str]], typer.Option("--exclude", "-e", help="Directory names to exclude")
    ] = None,
) -> None:
    try:
        validated_path = _validate_path(path)
        cli_output = to_tree(validated_path, incl_ext=include, excl_dir=exclude)
        console.print(cli_output)
    except Exception as e:
        console.print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-llm")
def cli_to_llm(
    path: Optional[str] = typer.Argument(None, help="Input a directory path"),
    output_file: str = typer.Option("llm.txt", "--output", "-o", help="Output file name"),
) -> None:
    """Generate (and export) the llm.txt file."""
    try:
        file_paths = parse_directory(path)
        cli_output = to_llm(file_paths, output_file=output_file)
        console.print(f"Exported to: {cli_output}")
    except Exception as e:
        console.print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-requirements")
def cli_to_requirements(
    path: Optional[str] = typer.Argument(None, help="Input a directory path"),
    output_file: str = typer.Option("requirements.txt", "--output", "-o", help="Output file name"),
) -> None:
    """Generate (and export) the requirements.txt file."""
    try:
        file_paths = parse_directory(path, include=[".py"])
        cli_output = to_requirements(file_paths, output_file=output_file)
        console.print(f"Exported to: {cli_output}")
    except Exception as e:
        console.print(f"Error: {e}")
        raise typer.Exit(1)


def _validate_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value).resolve() if value else pathlib.Path.cwd()

    if not path.exists():
        raise typer.BadParameter(f"No such file or directory: {path}")
        # raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise typer.BadParameter(f"Path is not a directory: {path}")
        # raise NotADirectoryError(f"Path is not a directory: {path}")

    return path
