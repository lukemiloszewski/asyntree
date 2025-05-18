import pathlib

from typer.testing import CliRunner

from asyntree import cli


class Test_CLI:
    def test_help(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["--help"])
        assert result.exit_code == 0
        assert "Input a directory or file path" in result.stdout

    def test_missing_path_argument(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app)
        assert result.exit_code == 2
        assert "Missing argument 'PATH'" in result.stdout

    def test_process_directory(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        result = fixt_cli_runner.invoke(cli.app, [str(fixt_python_project)])
        assert result.exit_code == 0
        assert "test_file.py" in result.stdout

    def test_process_file(
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path
    ) -> None:
        file_path = fixt_python_project / "test_file.py"
        result = fixt_cli_runner.invoke(cli.app, [str(file_path)])
        assert result.exit_code == 0
        assert "path" in result.stdout
        assert "ast" in result.stdout
        assert "test_file.py" in result.stdout

    def test_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["/path/does/not/exist"])
        assert result.exit_code != 0 or "No such file or directory" in result.stdout
