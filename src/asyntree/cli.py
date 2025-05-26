import pathlib
from typing import Optional

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
    path: Optional[str] = typer.Argument(None, help="Input a directory path"),
) -> None:
    """Generate tree structure."""
    try:
        file_paths = parse_directory(path, include=[".py"])
        cli_output = to_tree(file_paths)
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
