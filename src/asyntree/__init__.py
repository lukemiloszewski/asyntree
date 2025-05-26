"""asyntree"""

import importlib.metadata

from asyntree.api import (
    analyze_directory,
    export_directory_contents,
    extract_dependencies,
    generate_requirements_txt,
    generate_tree_structure,
    process_ast,
)

__title__ = "asyntree"
__description__ = "Syntax trees and file utilities."

try:
    __version__ = importlib.metadata.version(__package__ or __title__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "analyze_directory",
    "export_directory_contents",
    "extract_dependencies",
    "generate_requirements_txt",
    "generate_tree_structure",
    "process_ast",
]
