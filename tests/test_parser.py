import ast
from pathlib import Path

import pytest

from asyntree.parser import parse_path, parse_tree


class TestParsePath:
    def test_parse_path_directory(self, fixt_complex_python_project):
        """Test parsing a directory path."""
        paths = parse_path(str(fixt_complex_python_project))

        assert isinstance(paths, list)
        assert len(paths) > 0
        assert all(isinstance(p, Path) for p in paths)
        assert all(p.suffix == ".py" for p in paths)

        # Should find all Python files
        path_names = [p.name for p in paths]
        assert "main.py" in path_names
        assert "helpers.py" in path_names

    def test_parse_path_single_file(self, fixt_single_python_file):
        """Test parsing a single file path."""
        paths = parse_path(str(fixt_single_python_file))

        assert isinstance(paths, list)
        assert len(paths) == 1
        assert paths[0].name == "single_file.py"

    def test_parse_path_nonexistent_path(self):
        """Test parsing a nonexistent path."""
        with pytest.raises(SystemExit) as exc_info:
            parse_path("/path/does/not/exist")

        assert isinstance(exc_info.type, SystemExit)

    def test_parse_path_empty_directory(self, fixt_empty_directory):
        """Test parsing an empty directory."""
        paths = parse_path(str(fixt_empty_directory))

        assert isinstance(paths, list)
        assert len(paths) == 0

    def test_parse_path_directory_with_subdirectories(self, fixt_complex_python_project):
        """Test parsing directory with subdirectories (recursive)."""
        paths = parse_path(str(fixt_complex_python_project))

        # Should find files in subdirectories too
        path_strings = [str(p) for p in paths]
        assert any("utils" in path_str for path_str in path_strings)

    def test_parse_path_relative_path(self, fixt_python_project, monkeypatch):
        """Test parsing with relative path."""
        # Change to parent directory and use relative path
        parent_dir = fixt_python_project.parent
        monkeypatch.chdir(parent_dir)

        relative_path = fixt_python_project.name
        paths = parse_path(relative_path)

        assert isinstance(paths, list)
        assert len(paths) > 0
        assert all(p.is_absolute() for p in paths)  # Should resolve to absolute paths


class TestParseTree:
    def test_parse_tree_valid_python_file(self, fixt_single_python_file):
        """Test parsing a valid Python file."""
        tree = parse_tree(fixt_single_python_file)

        assert isinstance(tree, ast.AST)
        assert isinstance(tree, ast.Module)

    def test_parse_tree_simple_function(self, fixt_python_project):
        """Test parsing a simple Python file with function."""
        python_file = fixt_python_project / "test_file.py"
        tree = parse_tree(python_file)

        assert isinstance(tree, ast.Module)
        # Should contain function definition
        function_defs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(function_defs) > 0
        assert function_defs[0].name == "hello_world"

    def test_parse_tree_complex_file(self, fixt_complex_python_project):
        """Test parsing a complex Python file with imports and classes."""
        main_file = fixt_complex_python_project / "main.py"
        tree = parse_tree(main_file)

        assert isinstance(tree, ast.Module)

        # Should contain imports
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import | ast.ImportFrom)]
        assert len(imports) > 0

        # Should contain function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(functions) > 0

    def test_parse_tree_invalid_syntax(self, fixt_invalid_python_file):
        """Test parsing a file with invalid syntax."""
        invalid_file = fixt_invalid_python_file / "invalid.py"

        with pytest.raises(SyntaxError):
            parse_tree(invalid_file)

    def test_parse_tree_empty_file(self, tmp_path):
        """Test parsing an empty Python file."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        tree = parse_tree(empty_file)

        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 0

    def test_parse_tree_file_with_encoding(self, tmp_path):
        """Test parsing a file with specific encoding."""
        encoded_file = tmp_path / "encoded.py"
        # Write file with UTF-8 BOM and special characters
        encoded_file.write_bytes(
            b"\xef\xbb\xbf# -*- coding: utf-8 -*-\n# Comment with special chars: \xc3\xa9\xc3\xa0\xc3\xa8\ndef test(): pass\n"
        )

        tree = parse_tree(encoded_file)

        assert isinstance(tree, ast.Module)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(functions) == 1
        assert functions[0].name == "test"

    def test_parse_tree_nonexistent_file(self, tmp_path):
        """Test parsing a nonexistent file."""
        nonexistent_file = tmp_path / "does_not_exist.py"

        with pytest.raises(FileNotFoundError):
            parse_tree(nonexistent_file)

    def test_parse_tree_binary_file(self, fixt_binary_file):
        """Test parsing a binary file (should raise an error)."""
        binary_file = fixt_binary_file / "binary.dat"

        with pytest.raises((UnicodeDecodeError, SyntaxError)):
            parse_tree(binary_file)
