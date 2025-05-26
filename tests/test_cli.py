import pathlib
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from asyntree import cli


class TestCLI:
    def test_help(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["--help"])
        assert result.exit_code == 0
        assert "analyze" in result.stdout
        assert "tree" in result.stdout
        assert "export" in result.stdout
        assert "deps" in result.stdout

    def test_analyze_command(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["analyze", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "test_file.py" in result.stdout

    def test_analyze_single_file(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        file_path = fixt_python_project / "test_file.py"
        result = fixt_cli_runner.invoke(cli.app, ["analyze", str(file_path)])
        assert result.exit_code == 0
        assert "path" in result.stdout
        assert "ast" in result.stdout
        assert "test_file.py" in result.stdout

    def test_tree_command(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["tree", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "test_file.py" in result.stdout
        assert "test_folder" in result.stdout

    def test_export_command(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.txt"
            result = fixt_cli_runner.invoke(
                cli.app, ["export", str(fixt_python_project), "--output", str(output_file)]
            )
            assert result.exit_code == 0
            assert "Exported to:" in result.stdout
            assert output_file.exists()

            content = output_file.read_text()
            assert "Directory Export:" in content
            assert "Directory Structure" in content
            assert "File Contents" in content
            assert "test_file.py" in content
            assert "def hello_world():" in content

    def test_deps_command_show_only(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "with_imports.py"
        import_file.write_text("import os\nimport json\nfrom pathlib import Path\nimport requests")

        result = fixt_cli_runner.invoke(cli.app, ["deps", str(fixt_python_project), "--show"])
        assert result.exit_code == 0
        assert "Found" in result.stdout
        assert "dependencies" in result.stdout

    def test_deps_command_generate_file(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "with_imports.py"
        import_file.write_text("import requests\nimport pandas\nfrom flask import Flask")

        result = fixt_cli_runner.invoke(cli.app, ["deps", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "Generated requirements.txt" in result.stdout

    def test_requirements_command(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "with_imports.py"
        import_file.write_text("import numpy\nimport matplotlib.pyplot as plt")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "custom_requirements.txt"
            result = fixt_cli_runner.invoke(
                cli.app, ["requirements", str(fixt_python_project), "--output", str(output_file)]
            )
            assert result.exit_code == 0
            assert "Generated" in result.stdout
            assert output_file.exists()

            content = output_file.read_text()
            assert "# Generated requirements.txt" in content

    def test_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["analyze", "/path/does/not/exist"])
        assert result.exit_code != 0

    def test_tree_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["tree", "/path/does/not/exist"])
        assert result.exit_code != 0
