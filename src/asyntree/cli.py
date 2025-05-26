import sys

import typer
from rich.console import Console
from rich.pretty import pprint

from asyntree.api import (
    analyze_directory,
    export_directory_contents,
    extract_dependencies,
    generate_requirements_txt,
    generate_tree_structure,
)

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def describe(
    path: str = typer.Argument(..., help="Input a directory or file path"),
) -> None:
    """Analyze Python files and show AST node counts."""
    try:
        output = analyze_directory(path)
        pprint(output, max_length=50)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("to-tree")
def to_tree(
    path: str = typer.Argument(..., help="Input a directory path"),
) -> None:
    """Display the tree structure of a directory."""
    try:
        tree_lines = generate_tree_structure(path)
        for line in tree_lines:
            console.print(line)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("to-llm")
def to_llm(
    path: str = typer.Argument(..., help="Input a directory or file path"),
    output: str = typer.Option("llm.txt", "--output", "-o", help="Output file name"),
) -> None:
    """Export directory contents to a markdown file for LLM consumption."""
    try:
        output_path = export_directory_contents(path, output)
        console.print(f"[green]Exported to: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("to-requirements")
def to_requirements(
    path: str = typer.Argument(..., help="Input a directory path"),
    output: str = typer.Option("requirements.txt", "--output", "-o", help="Output file name"),
) -> None:
    """Generate a requirements.txt file from Python imports."""
    try:
        output_path = generate_requirements_txt(path, output)
        dependencies = extract_dependencies(path)

        console.print(f"[green]Generated {output}: {output_path}[/green]")
        console.print(f"[blue]Found {len(dependencies)} unique dependencies[/blue]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        console.print("[yellow]No command provided. Use --help to see available commands.[/yellow]")
        raise typer.Exit(1)

    app()


if __name__ == "__main__":
    main()
