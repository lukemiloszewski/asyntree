import sys
from pathlib import Path

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
def analyze(
    path: str = typer.Argument(..., help="Input a directory or file path"),
) -> None:
    """Analyze Python files and show AST node counts."""
    try:
        output = analyze_directory(path)
        pprint(output, max_length=50)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def tree(
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


@app.command()
def export(
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


@app.command()
def deps(
    path: str = typer.Argument(..., help="Input a directory path"),
    show_only: bool = typer.Option(
        False, "--show", "-s", help="Only show dependencies, don't generate file"
    ),
) -> None:
    """Extract Python dependencies from import statements."""
    try:
        dependencies = extract_dependencies(path)

        if not dependencies:
            console.print("[yellow]No external dependencies found.[/yellow]")
            return

        console.print(f"[blue]Found {len(dependencies)} dependencies:[/blue]")
        for dep in sorted(dependencies):
            console.print(f"  • {dep}")

        if not show_only:
            output_path = generate_requirements_txt(path)
            console.print(f"\n[green]Generated requirements.txt: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def requirements(
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
    """Main entry point - defaults to analyze command for backward compatibility."""
    # If no subcommand is provided, default to analyze
    if len(sys.argv) == 1:
        console.print("[yellow]No command provided. Use --help to see available commands.[/yellow]")
        raise typer.Exit(1)

    # Check if the first argument is a path (for backward compatibility)
    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        path_arg = sys.argv[1]
        if Path(path_arg).exists() or path_arg in ["--help", "-h"]:
            # This looks like a path or help, let typer handle it normally
            app()
        else:
            app()
    else:
        app()


if __name__ == "__main__":
    main()
