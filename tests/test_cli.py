import pathlib
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from asyntree import cli


class TestCLIHelp:
    def test_help(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["--help"])
        assert result.exit_code == 0
        assert "describe" in result.stdout
        assert "to-tree" in result.stdout
        assert "to-llm" in result.stdout
        assert "to-requirements" in result.stdout


class TestDescribeCommand:
    def test_describe_directory(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["describe", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "test_file.py" in result.stdout

    def test_describe_single_file(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        file_path = fixt_python_project / "test_file.py"
        result = fixt_cli_runner.invoke(cli.app, ["describe", str(file_path)])
        assert result.exit_code == 0
        assert "path" in result.stdout
        assert "ast" in result.stdout
        assert "test_file.py" in result.stdout

    def test_describe_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["describe", "/path/does/not/exist"])
        assert result.exit_code != 0


class TestToTreeCommand:
    def test_to_tree_directory(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-tree", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "test_file.py" in result.stdout
        assert "test_folder" in result.stdout

    def test_to_tree_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-tree", "/path/does/not/exist"])
        assert result.exit_code != 0


class TestToLLMCommand:
    def test_to_llm_directory(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.txt"
            result = fixt_cli_runner.invoke(
                cli.app, ["to-llm", str(fixt_python_project), "--output", str(output_file)]
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

    def test_to_llm_default_output(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-llm", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "Exported to:" in result.stdout

    def test_to_llm_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-llm", "/path/does/not/exist"])
        assert result.exit_code != 0


class TestToRequirementsCommand:
    def test_to_requirements_with_imports(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "with_imports.py"
        import_file.write_text("import requests\nimport pandas\nfrom flask import Flask")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "custom_requirements.txt"
            result = fixt_cli_runner.invoke(
                cli.app, ["to-requirements", str(fixt_python_project), "--output", str(output_file)]
            )
            assert result.exit_code == 0
            assert "Generated" in result.stdout
            assert output_file.exists()

            content = output_file.read_text()
            assert "# Generated requirements.txt" in content

    def test_to_requirements_default_output(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "with_imports.py"
        import_file.write_text("import numpy\nimport matplotlib.pyplot as plt")

        result = fixt_cli_runner.invoke(cli.app, ["to-requirements", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "Generated" in result.stdout

    def test_to_requirements_no_external_deps(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        import_file = fixt_python_project / "stdlib_only.py"
        import_file.write_text("import os\nimport sys\nfrom pathlib import Path")

        result = fixt_cli_runner.invoke(cli.app, ["to-requirements", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "Generated" in result.stdout

    def test_to_requirements_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-requirements", "/path/does/not/exist"])
        assert result.exit_code != 0
