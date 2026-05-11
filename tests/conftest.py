"""Shared pytest fixtures for the henryk_analysis test suite."""
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_recordings_df() -> pd.DataFrame:
    """Minimal recordings stats DataFrame for parquet round-trip tests."""
    return pd.DataFrame(
        {
            "filename": ["rec01.opus", "rec02.opus"],
            "duration_seconds": [120.5, 60.0],
            "size_bytes": [1024, 2048],
        }
    )


@pytest.fixture
def project_root() -> Path:
    """Resolved path to the project root (where pyproject.toml lives)."""
    from henryk_analysis.config import PROJ_ROOT

    return PROJ_ROOT
