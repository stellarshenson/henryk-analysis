"""Tests for henryk_analysis.utils helpers."""
from pathlib import Path

import pytest

from henryk_analysis.utils import (
    get_file_name_without_extension,
    get_truncated_string,
)


@pytest.mark.parametrize(
    "input_path,expected",
    [
        ("foo.txt", "foo"),
        ("/path/to/bar.parquet", "bar"),
        ("file.tar.gz", "file.tar"),
        (Path("baz.json"), "baz"),
        (Path("/a/b/c.csv"), "c"),
    ],
)
def test_get_file_name_without_extension(input_path, expected):
    assert get_file_name_without_extension(input_path) == expected


def test_get_truncated_string_under_limit_unchanged():
    assert get_truncated_string("hello", max_length=10) == "hello"


def test_get_truncated_string_at_limit_unchanged():
    text = "x" * 10
    assert get_truncated_string(text, max_length=10) == text


def test_get_truncated_string_over_limit_adds_ellipsis():
    result = get_truncated_string("x" * 100, max_length=10)
    assert result == "x" * 10 + "..."
    assert len(result) == 13


def test_get_truncated_string_default_max_length_is_50():
    result = get_truncated_string("x" * 60)
    assert result == "x" * 50 + "..."
