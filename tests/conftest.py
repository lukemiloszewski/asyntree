import pathlib

import pytest
from typer.testing import CliRunner


@pytest.fixture
def fixt_cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fixt_python_project(tmp_path) -> pathlib.Path:
    project_dir = tmp_path / "test_folder"
    project_dir.mkdir()

    python_file = project_dir / "test_file.py"
    python_file.write_text("def hello_world(): return 'Hello, World!'")

    return project_dir
