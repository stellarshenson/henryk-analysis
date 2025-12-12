"""
Dataset generation and loading utilities for henryk analysis project.

Provides functions for loading and processing recordings data.
"""
from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from lib_henryk_analysis.config import (
    DIR_RECORDINGS,
    FILE_RECORDINGS_STATS_PARQUET,
    FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET,
    FILE_TRANSCRIPTIONS_PARQUET,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)

app = typer.Typer()


def load_recordings_stats(
    path: Path = FILE_RECORDINGS_STATS_PARQUET,
) -> pd.DataFrame:
    """
    Load recordings statistics from parquet file.

    Parameters
    ----------
    path : Path
        Path to the parquet file.

    Returns
    -------
    pd.DataFrame
        DataFrame with recordings statistics.
    """
    if not path.exists():
        logger.warning(f"Recordings stats file not found: {path}")
        return pd.DataFrame()

    logger.info(f"Loading recordings stats from {path}")
    return pd.read_parquet(path)


def load_transcriptions(
    path: Path = FILE_TRANSCRIPTIONS_PARQUET,
) -> pd.DataFrame:
    """
    Load transcriptions from parquet file.

    Parameters
    ----------
    path : Path
        Path to the parquet file.

    Returns
    -------
    pd.DataFrame
        DataFrame with transcriptions.
    """
    if not path.exists():
        logger.warning(f"Transcriptions file not found: {path}")
        return pd.DataFrame()

    logger.info(f"Loading transcriptions from {path}")
    return pd.read_parquet(path)


def load_classifications(
    path: Path = FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET,
) -> pd.DataFrame:
    """
    Load transcription classifications from parquet file.

    Parameters
    ----------
    path : Path
        Path to the parquet file.

    Returns
    -------
    pd.DataFrame
        DataFrame with classifications.
    """
    if not path.exists():
        logger.warning(f"Classifications file not found: {path}")
        return pd.DataFrame()

    logger.info(f"Loading classifications from {path}")
    return pd.read_parquet(path)


def save_dataframe(
    df: pd.DataFrame,
    path: Path,
    overwrite: bool = False,
) -> None:
    """
    Save DataFrame to parquet file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    path : Path
        Output path.
    overwrite : bool
        Whether to overwrite existing file.
    """
    if path.exists() and not overwrite:
        logger.warning(f"File exists and overwrite=False: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    logger.info(f"Saved {len(df)} records to {path}")


@app.command()
def generate_stats(
    input_path: Path = DIR_RECORDINGS,
    output_path: Path = FILE_RECORDINGS_STATS_PARQUET,
) -> None:
    """
    Generate recordings statistics from raw audio files.

    Parameters
    ----------
    input_path : Path
        Path to recordings directory.
    output_path : Path
        Output path for parquet file.
    """
    from lib_henryk_analysis.recordings import recordings

    logger.info(f"Generating recordings stats from {input_path}")
    df = recordings.get_recordings_info(input_path)
    save_dataframe(df, output_path, overwrite=True)
    logger.success(f"Generated stats for {len(df)} recordings")


@app.command()
def info() -> None:
    """Display information about available datasets."""
    datasets = [
        ("Recordings Stats", FILE_RECORDINGS_STATS_PARQUET),
        ("Transcriptions", FILE_TRANSCRIPTIONS_PARQUET),
        ("Classifications", FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET),
    ]

    logger.info("Available datasets:")
    for name, path in datasets:
        if path.exists():
            df = pd.read_parquet(path)
            logger.info(f"  {name}: {len(df)} records ({path.name})")
        else:
            logger.warning(f"  {name}: NOT FOUND ({path.name})")


if __name__ == "__main__":
    app()
