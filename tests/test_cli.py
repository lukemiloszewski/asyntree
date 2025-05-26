import pathlib

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

    def test_describe_with_exception(
        self, fixt_cli_runner: CliRunner, fixt_invalid_python_file: pathlib.Path
    ) -> None:
        """Test describe command with files that cause parsing errors."""
        result = fixt_cli_runner.invoke(cli.app, ["describe", str(fixt_invalid_python_file)])
        assert result.exit_code == 1
        assert "Error:" in result.stdout


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

    def test_to_tree_single_file(
        self, fixt_cli_runner: CliRunner, fixt_single_python_file: pathlib.Path
    ) -> None:
        """Test to-tree command with a single file."""
        result = fixt_cli_runner.invoke(cli.app, ["to-tree", str(fixt_single_python_file)])
        assert result.exit_code == 0
        assert "single_file.py" in result.stdout

    def test_to_tree_with_generic_exception(self, fixt_cli_runner: CliRunner, monkeypatch) -> None:
        """Test to-tree command with a generic exception (not FileNotFoundError)."""
        from asyntree import api

        def mock_generate_tree_structure(path):
            raise ValueError("Mock error")

        monkeypatch.setattr(api, "generate_tree_structure", mock_generate_tree_structure)

        result = fixt_cli_runner.invoke(cli.app, ["to-tree", "/some/path"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestToLLMCommand:
    def test_to_llm_directory(
        self,
        fixt_cli_runner: CliRunner,
        fixt_python_project: pathlib.Path,
        fixt_temp_output_dir: pathlib.Path,
    ) -> None:
        output_file = fixt_temp_output_dir / "export.txt"
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
        self, fixt_cli_runner: CliRunner, fixt_python_project: pathlib.Path, tmp_path, monkeypatch
    ) -> None:
        # Change to temporary directory to ensure default output goes there
        monkeypatch.chdir(tmp_path)

        result = fixt_cli_runner.invoke(cli.app, ["to-llm", str(fixt_python_project)])
        assert result.exit_code == 0
        assert "Exported to:" in result.stdout

        # Check that the default file was created in the temp directory
        default_output = tmp_path / "llm.txt"
        assert default_output.exists()

    def test_to_llm_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-llm", "/path/does/not/exist"])
        assert result.exit_code != 0

    def test_to_llm_with_exception(
        self, fixt_cli_runner: CliRunner, fixt_temp_output_dir: pathlib.Path, monkeypatch
    ) -> None:
        """Test to-llm command with an exception during export."""
        from asyntree import api

        def mock_export_directory_contents(path, output):
            raise PermissionError("Mock permission error")

        monkeypatch.setattr(api, "export_directory_contents", mock_export_directory_contents)

        output_file = fixt_temp_output_dir / "test.txt"
        result = fixt_cli_runner.invoke(
            cli.app, ["to-llm", "/some/path", "--output", str(output_file)]
        )
        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestToRequirementsCommand:
    def test_to_requirements_with_imports(
        self,
        fixt_cli_runner: CliRunner,
        fixt_complex_python_project: pathlib.Path,
        fixt_temp_output_dir: pathlib.Path,
    ) -> None:
        output_file = fixt_temp_output_dir / "custom_requirements.txt"
        result = fixt_cli_runner.invoke(
            cli.app,
            ["to-requirements", str(fixt_complex_python_project), "--output", str(output_file)],
        )
        assert result.exit_code == 0
        assert "Generated" in result.stdout
        assert output_file.exists()

        content = output_file.read_text()
        assert "# Generated requirements.txt" in content

    def test_to_requirements_default_output(
        self,
        fixt_cli_runner: CliRunner,
        fixt_complex_python_project: pathlib.Path,
        tmp_path,
        monkeypatch,
    ) -> None:
        # Change to temporary directory to ensure default output goes there
        monkeypatch.chdir(tmp_path)

        result = fixt_cli_runner.invoke(
            cli.app, ["to-requirements", str(fixt_complex_python_project)]
        )
        assert result.exit_code == 0
        assert "Generated" in result.stdout

        # Check that the default file was created in the temp directory
        default_output = tmp_path / "requirements.txt"
        assert default_output.exists()

    def test_to_requirements_no_external_deps(
        self,
        fixt_cli_runner: CliRunner,
        fixt_python_project: pathlib.Path,
        fixt_temp_output_dir: pathlib.Path,
    ) -> None:
        output_file = fixt_temp_output_dir / "no_deps.txt"
        result = fixt_cli_runner.invoke(
            cli.app, ["to-requirements", str(fixt_python_project), "--output", str(output_file)]
        )
        assert result.exit_code == 0
        assert "Generated" in result.stdout

    def test_to_requirements_nonexistent_path(self, fixt_cli_runner: CliRunner) -> None:
        result = fixt_cli_runner.invoke(cli.app, ["to-requirements", "/path/does/not/exist"])
        assert result.exit_code != 0

    def test_to_requirements_with_exception(
        self, fixt_cli_runner: CliRunner, fixt_temp_output_dir: pathlib.Path, monkeypatch
    ) -> None:
        """Test to-requirements command with an exception during generation."""
        from asyntree import api

        def mock_generate_requirements_txt(path, output):
            raise OSError("Mock OS error")

        monkeypatch.setattr(api, "generate_requirements_txt", mock_generate_requirements_txt)

        output_file = fixt_temp_output_dir / "test_req.txt"
        result = fixt_cli_runner.invoke(
            cli.app, ["to-requirements", "/some/path", "--output", str(output_file)]
        )
        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestMainFunction:
    def test_main_no_args(self, fixt_cli_runner: CliRunner) -> None:
        """Test main function with no arguments."""
        result = fixt_cli_runner.invoke(cli.app, [])
        assert result.exit_code == 1
        assert "No command provided" in result.stdout
