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


@pytest.fixture
def fixt_complex_python_project(tmp_path) -> pathlib.Path:
    project_dir = tmp_path / "complex_project"
    project_dir.mkdir()

    main_file = project_dir / "main.py"
    main_file.write_text("""
import os
import sys
import requests
import pandas as pd
from flask import Flask

def main():
    app = Flask(__name__)
    return app

if __name__ == "__main__":
    main()
""")

    subdir = project_dir / "utils"
    subdir.mkdir()

    utils_file = subdir / "helpers.py"
    utils_file.write_text("""
import json
import numpy as np
from datetime import datetime

class Helper:
    def __init__(self):
        self.data = {}

    def process_data(self, data):
        return json.dumps(data)
""")

    init_file = subdir / "__init__.py"
    init_file.write_text("")

    readme_file = project_dir / "README.md"
    readme_file.write_text("# Test Project\n\nThis is a test project.")

    return project_dir


@pytest.fixture
def fixt_temp_output_dir(tmp_path) -> pathlib.Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def fixt_invalid_python_file(tmp_path) -> pathlib.Path:
    project_dir = tmp_path / "invalid_project"
    project_dir.mkdir()

    invalid_file = project_dir / "invalid.py"
    invalid_file.write_text("def broken_function(\n    return 'missing colon and parenthesis'")

    return project_dir


@pytest.fixture
def fixt_binary_file(tmp_path) -> pathlib.Path:
    project_dir = tmp_path / "binary_project"
    project_dir.mkdir()

    binary_file = project_dir / "binary.dat"
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")

    return project_dir


@pytest.fixture
def fixt_empty_directory(tmp_path) -> pathlib.Path:
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    return empty_dir


@pytest.fixture
def fixt_single_python_file(tmp_path) -> pathlib.Path:
    python_file = tmp_path / "single_file.py"
    python_file.write_text("""
import os
import requests
from typing import List, Dict

def example_function(data: List[Dict]) -> str:
    \"\"\"Example function with type hints.\"\"\"
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(str(item))
    return ', '.join(result)

class ExampleClass:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name
""")
    return python_file
