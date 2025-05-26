import ast
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from asyntree.api import (
    analyze_directory,
    export_directory_contents,
    extract_dependencies,
    generate_requirements_txt,
    generate_tree_structure,
    process_ast,
)
from asyntree.visitor import Visitor


class TestProcessAst:
    def test_process_ast_basic(self):
        """Test process_ast with a simple AST."""
        code = "def hello(): return 'world'"
        tree = ast.parse(code)
        visitor = Visitor()

        result = process_ast(tree, visitor)

        assert isinstance(result, dict)
        assert "FunctionDef" in result
        assert "Return" in result
        assert result["FunctionDef"] >= 1


class TestAnalyzeDirectory:
    def test_analyze_directory_success(self, fixt_python_project):
        """Test successful directory analysis."""
        result = analyze_directory(str(fixt_python_project))

        assert isinstance(result, list)
        assert len(result) > 0
        assert "path" in result[0]
        assert "ast" in result[0]
        assert result[0]["path"] == "test_file.py"

    def test_analyze_directory_single_file(self, fixt_single_python_file):
        """Test analyzing a single file."""
        result = analyze_directory(str(fixt_single_python_file))

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["path"] == "single_file.py"

    def test_analyze_directory_nonexistent_path(self):
        """Test analyze_directory with nonexistent path."""
        with pytest.raises(SystemExit):
            analyze_directory("/path/does/not/exist")

    def test_analyze_directory_with_parsing_error(self, fixt_invalid_python_file):
        """Test analyze_directory with files that cause parsing errors."""
        with pytest.raises(SyntaxError):
            analyze_directory(str(fixt_invalid_python_file))


class TestGenerateTreeStructure:
    def test_generate_tree_structure_directory(self, fixt_complex_python_project):
        """Test tree structure generation for a directory."""
        result = generate_tree_structure(str(fixt_complex_python_project))

        assert isinstance(result, list)
        assert len(result) > 0
        assert any("complex_project/" in line for line in result)
        assert any("main.py" in line for line in result)
        assert any("utils/" in line for line in result)

    def test_generate_tree_structure_single_file(self, fixt_single_python_file):
        """Test tree structure generation for a single file."""
        result = generate_tree_structure(str(fixt_single_python_file))

        assert isinstance(result, list)
        assert len(result) == 1
        assert "single_file.py" in result[0]

    def test_generate_tree_structure_nonexistent_path(self):
        """Test tree structure generation with nonexistent path."""
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            generate_tree_structure("/path/does/not/exist")

    def test_generate_tree_structure_empty_directory(self, fixt_empty_directory):
        """Test tree structure generation for empty directory."""
        result = generate_tree_structure(str(fixt_empty_directory))

        assert isinstance(result, list)
        assert len(result) == 1
        assert "empty_dir/" in result[0]


class TestExportDirectoryContents:
    def test_export_directory_contents_success(self, fixt_python_project, fixt_temp_output_dir):
        """Test successful directory export."""
        output_file = fixt_temp_output_dir / "test_export.txt"

        result_path = export_directory_contents(str(fixt_python_project), str(output_file))

        assert Path(result_path).exists()
        content = Path(result_path).read_text()
        assert "Directory Export:" in content
        assert "Directory Structure" in content
        assert "File Contents" in content
        assert "test_file.py" in content
        assert "def hello_world()" in content

    def test_export_directory_contents_single_file(
        self, fixt_single_python_file, fixt_temp_output_dir
    ):
        """Test exporting a single file."""
        output_file = fixt_temp_output_dir / "single_export.txt"

        result_path = export_directory_contents(str(fixt_single_python_file), str(output_file))

        assert Path(result_path).exists()
        content = Path(result_path).read_text()
        assert "single_file.py" in content

    def test_export_directory_contents_nonexistent_path(self, fixt_temp_output_dir):
        """Test export with nonexistent path."""
        output_file = fixt_temp_output_dir / "fail_export.txt"

        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            export_directory_contents("/path/does/not/exist", str(output_file))

    def test_export_directory_contents_default_output(
        self, fixt_python_project, tmp_path, monkeypatch
    ):
        """Test export with default output filename."""
        monkeypatch.chdir(tmp_path)

        result_path = export_directory_contents(str(fixt_python_project))

        assert Path(result_path).exists()
        assert Path(result_path).name == "llm.txt"

    def test_export_directory_contents_with_different_file_types(
        self, fixt_complex_python_project, fixt_temp_output_dir
    ):
        """Test export with various file types."""
        output_file = fixt_temp_output_dir / "complex_export.txt"

        result_path = export_directory_contents(str(fixt_complex_python_project), str(output_file))

        content = Path(result_path).read_text()
        assert "```python" in content  # Python files
        assert "```markdown" in content  # Markdown files

    def test_export_directory_contents_permission_error(
        self, fixt_python_project, fixt_temp_output_dir
    ):
        """Test export handling permission errors when reading files."""
        output_file = fixt_temp_output_dir / "permission_export.txt"

        # Mock a file that raises PermissionError
        with patch("builtins.open", side_effect=PermissionError("Permission denied")) as mock_file:
            # Only mock for specific calls, allow the output file to be written
            def side_effect(*args, **kwargs):
                if str(output_file) in str(args[0]):
                    return mock_open()(*args, **kwargs)
                raise PermissionError("Permission denied")

            mock_file.side_effect = side_effect

            result_path = export_directory_contents(str(fixt_python_project), str(output_file))
            content = Path(result_path).read_text()
            assert "Could not read file:" in content

    def test_export_directory_contents_unicode_error(self, fixt_binary_file, fixt_temp_output_dir):
        """Test export handling Unicode decode errors."""
        output_file = fixt_temp_output_dir / "unicode_export.txt"

        result_path = export_directory_contents(str(fixt_binary_file), str(output_file))

        content = Path(result_path).read_text()
        assert "Could not read file:" in content


class TestExtractDependencies:
    def test_extract_dependencies_with_imports(self, fixt_complex_python_project):
        """Test dependency extraction with various import types."""
        dependencies = extract_dependencies(str(fixt_complex_python_project))

        assert isinstance(dependencies, set)
        assert len(dependencies) > 0
        assert "requests" in dependencies
        assert "pandas" in dependencies
        assert "flask" in dependencies
        assert "json" in dependencies
        assert "numpy" in dependencies

    def test_extract_dependencies_no_imports(self, fixt_python_project):
        """Test dependency extraction with no imports."""
        dependencies = extract_dependencies(str(fixt_python_project))

        assert isinstance(dependencies, set)
        # Should be empty or only contain standard library modules

    def test_extract_dependencies_single_file(self, fixt_single_python_file):
        """Test dependency extraction from single file."""
        dependencies = extract_dependencies(str(fixt_single_python_file))

        assert isinstance(dependencies, set)
        assert "requests" in dependencies
        assert "typing" in dependencies

    def test_extract_dependencies_nonexistent_path(self):
        """Test dependency extraction with nonexistent path."""
        with pytest.raises(SystemExit):
            extract_dependencies("/path/does/not/exist")


class TestGenerateRequirementsTxt:
    def test_generate_requirements_txt_with_external_deps(
        self, fixt_complex_python_project, fixt_temp_output_dir
    ):
        """Test requirements.txt generation with external dependencies."""
        output_file = fixt_temp_output_dir / "test_requirements.txt"

        result_path = generate_requirements_txt(str(fixt_complex_python_project), str(output_file))

        assert Path(result_path).exists()
        content = Path(result_path).read_text()
        assert "# Generated requirements.txt" in content
        assert "requests" in content
        assert "pandas" in content
        assert "flask" in content
        assert "numpy" in content
        # Standard library modules should not be included
        assert "os" not in content or content.count("os\n") == 0
        assert "sys" not in content or content.count("sys\n") == 0

    def test_generate_requirements_txt_no_external_deps(
        self, fixt_python_project, fixt_temp_output_dir
    ):
        """Test requirements.txt generation with no external dependencies."""
        output_file = fixt_temp_output_dir / "empty_requirements.txt"

        result_path = generate_requirements_txt(str(fixt_python_project), str(output_file))

        assert Path(result_path).exists()
        content = Path(result_path).read_text()
        assert "# Generated requirements.txt" in content

    def test_generate_requirements_txt_default_output(
        self, fixt_complex_python_project, tmp_path, monkeypatch
    ):
        """Test requirements.txt generation with default filename."""
        monkeypatch.chdir(tmp_path)

        result_path = generate_requirements_txt(str(fixt_complex_python_project))

        assert Path(result_path).exists()
        assert Path(result_path).name == "requirements.txt"

    def test_generate_requirements_txt_stdlib_filtering(self, tmp_path):
        """Test that standard library modules are properly filtered out."""
        # Create a test file with only stdlib imports
        test_dir = tmp_path / "stdlib_test"
        test_dir.mkdir()

        test_file = test_dir / "stdlib_only.py"
        test_file.write_text("""
import os
import sys
import json
import datetime
from pathlib import Path
from collections import Counter
""")

        output_file = tmp_path / "stdlib_requirements.txt"
        result_path = generate_requirements_txt(str(test_dir), str(output_file))

        content = Path(result_path).read_text()
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("#")
        ]

        # Should have no external dependencies, only comments
        external_deps = [line for line in lines if not line.startswith("#")]
        assert len(external_deps) == 0

    def test_generate_requirements_txt_duplicate_handling(self, tmp_path):
        """Test that duplicate dependencies are handled correctly."""
        test_dir = tmp_path / "duplicate_test"
        test_dir.mkdir()

        # Create multiple files with overlapping imports
        file1 = test_dir / "file1.py"
        file1.write_text("import requests\nimport pandas")

        file2 = test_dir / "file2.py"
        file2.write_text("import requests\nimport numpy")

        output_file = tmp_path / "dup_requirements.txt"
        result_path = generate_requirements_txt(str(test_dir), str(output_file))

        content = Path(result_path).read_text()
        # requests should only appear once
        assert content.count("requests\n") == 1
