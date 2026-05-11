"""Tests for henryk_analysis.dataset module - load/save parquet utilities."""
from pathlib import Path

import pandas as pd
import pytest

from henryk_analysis.dataset import (
    load_classifications,
    load_recordings_stats,
    load_transcriptions,
    save_dataframe,
)


@pytest.mark.parametrize(
    "loader", [load_recordings_stats, load_transcriptions, load_classifications]
)
def test_loader_returns_empty_df_when_path_missing(loader, tmp_path: Path):
    missing = tmp_path / "does-not-exist.parquet"
    df = loader(missing)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_save_and_load_roundtrip(tmp_path: Path, sample_recordings_df: pd.DataFrame):
    path = tmp_path / "out.parquet"
    save_dataframe(sample_recordings_df, path)

    assert path.exists()
    pd.testing.assert_frame_equal(pd.read_parquet(path), sample_recordings_df)


def test_save_dataframe_creates_parent_dirs(tmp_path: Path, sample_recordings_df):
    nested = tmp_path / "a" / "b" / "c" / "out.parquet"
    save_dataframe(sample_recordings_df, nested)
    assert nested.exists()


def test_save_dataframe_respects_overwrite_flag(tmp_path: Path):
    path = tmp_path / "out.parquet"
    save_dataframe(pd.DataFrame({"a": [1]}), path)

    save_dataframe(pd.DataFrame({"a": [2]}), path, overwrite=False)
    assert pd.read_parquet(path)["a"].iloc[0] == 1

    save_dataframe(pd.DataFrame({"a": [2]}), path, overwrite=True)
    assert pd.read_parquet(path)["a"].iloc[0] == 2
