"""Tests for henryk_analysis.config module - path constants and resolution."""
from pathlib import Path

import pytest


def test_proj_root_resolves_to_repository_root(project_root: Path):
    assert project_root.is_dir()
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "src" / "henryk_analysis" / "__init__.py").exists()


@pytest.mark.parametrize(
    "attr",
    [
        "DATA_DIR",
        "RAW_DATA_DIR",
        "INTERIM_DATA_DIR",
        "PROCESSED_DATA_DIR",
        "EXTERNAL_DATA_DIR",
        "MODELS_DIR",
        "REPORTS_DIR",
        "FIGURES_DIR",
        "RESOURCES_DIR",
    ],
)
def test_directory_constants_are_paths(attr):
    import henryk_analysis.config as config

    value = getattr(config, attr)
    assert isinstance(value, Path), f"{attr} is {type(value).__name__}, expected Path"


@pytest.mark.parametrize(
    "attr",
    [
        "FILE_RECORDINGS_STATS_PARQUET",
        "FILE_TRANSCRIPTIONS_PARQUET",
        "FILE_TRANSCRIPTIONS_JSON",
        "FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET",
        "FILE_TRANSCRIPTIONS_CLASSIFICATIONS_STATS_PARQUET",
        "FILE_TRANSCRIPTION_TEMPLATE",
        "FILE_PROMPT_RECORDING_CLASSIFICATION",
        "FILE_PROMPT_RECORDING_SUMMARY",
    ],
)
def test_file_constants_are_paths(attr):
    import henryk_analysis.config as config

    value = getattr(config, attr)
    assert isinstance(value, Path), f"{attr} is {type(value).__name__}, expected Path"


def test_figures_dir_under_reports_dir_by_default(monkeypatch):
    monkeypatch.delenv("FIGURES_DIR", raising=False)
    monkeypatch.delenv("REPORTS_DIR", raising=False)
    import importlib

    import henryk_analysis.config as config

    importlib.reload(config)
    assert config.FIGURES_DIR == config.REPORTS_DIR / "figures"


def test_env_override_for_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "custom_data"))
    import importlib

    import henryk_analysis.config as config

    importlib.reload(config)
    assert config.DATA_DIR == tmp_path / "custom_data"
