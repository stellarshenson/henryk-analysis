"""
General utilities for the henryk analysis project.
"""

from pathlib import Path


def get_file_name_without_extension(file_path: str | Path) -> str:
    """Extract filename without extension from a path."""
    if isinstance(file_path, Path):
        return file_path.stem
    file_name = file_path.split("/")[-1]
    file_name_without_extension = ".".join(file_name.split(".")[:-1])
    return file_name_without_extension


def get_truncated_string(text: str, max_length: int = 50) -> str:
    """Truncate string to max_length with ellipsis."""
    if len(text) > max_length:
        text = text[0:max_length] + "..."
    return text


# EOF
