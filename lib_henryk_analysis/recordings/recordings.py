"""
Performs retrieval of the recordings and their stats.
"""
import os
import re
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from mutagen import File as MutagenFile
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from lib_henryk_analysis import utils
from lib_henryk_analysis.config import DIR_RECORDINGS
from lib_henryk_analysis.logger import logger


def get_recordings_files_list(path_recordings: str | Path = DIR_RECORDINGS) -> list[str]:
    """Get list of all audio recording files (m4a and mp4)."""
    path_recordings = str(path_recordings)
    list_m4a = glob(f"{path_recordings}/**/*.m4a", recursive=True)
    list_mp4 = glob(f"{path_recordings}/**/*.mp4", recursive=True)
    return list_m4a + list_mp4


def get_recordings_names_df(path_recordings: str | Path = DIR_RECORDINGS) -> pd.DataFrame:
    """Get DataFrame with recording file paths, filenames, and names."""
    files_list = get_recordings_files_list(path_recordings)
    filenames_list = [os.path.basename(f) for f in files_list]
    names_list = [utils.get_file_name_without_extension(f) for f in files_list]

    df = pd.DataFrame(
        {
            "path": files_list,
            "file": filenames_list,
            "name": names_list,
        }
    )
    return df


def sort_df_by_date_inferred_from_name(df: pd.DataFrame, drop_date: bool = True) -> pd.DataFrame:
    """Sort DataFrame by date extracted from the 'name' column."""
    df = df.reset_index(drop=True)
    series_date = df["name"].str.extract(r"^.+ (\d+-\d+-\d+) .+$")[0]
    df["date"] = series_date
    df = df.sort_values(by="date")
    if drop_date:
        df.drop("date", axis=1, inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df


def get_recordings_info(path_recordings: str | Path) -> pd.DataFrame:
    """Load audio files and extract metadata into a DataFrame."""
    files_m4a = get_recordings_files_list(path_recordings=path_recordings)
    logger.info(f"retrieved {len(files_m4a)} files")

    df = pd.DataFrame(
        {
            "file": [],
            "name": [],
            "title": [],
            "kind": [],
            "date": [],
            "type": [],
            "duration": [],
        }
    )

    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[green]{task.percentage:>3.0f}%[/green]"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"Processing audio files", total=len(files_m4a))
        for f in files_m4a:
            audio_recording_info = get_audio_file_info(recording_file_path=f)
            if audio_recording_info is not None:
                df.loc[len(df)] = audio_recording_info
            progress.update(task, advance=1)

    df = df.sort_values(by="date")
    df = df.reset_index(drop=True)

    logger.info(f"generated stats for {len(df)} audio recordings")
    return df


def get_audio_file_info(recording_file_path: str) -> dict | None:
    """Get info from a file and process into a dictionary.

    Uses mutagen (pure Python) for audio metadata extraction.
    Supports m4a, mp4, mp3, and other common audio formats.
    """
    try:
        audio = MutagenFile(recording_file_path)
        if audio is None:
            logger.warning(f"mutagen could not read file: {recording_file_path}")
            return None

        _filename = os.path.basename(recording_file_path)
        _filename_regex_groups = re.search(
            r"^(.+) (\d+-\d+-\d+) (.+)\.(.+)$", _filename
        )

        if _filename_regex_groups is None:
            logger.warning(f"filename does not match expected pattern: {_filename}")
            return None

        _recording_kind = _filename_regex_groups[1]
        _recording_date = _filename_regex_groups[2]
        _recording_date = datetime.strptime(_recording_date, "%Y-%m-%d")
        _recording_name = ".".join(_filename.split(".")[:-1])
        _recording_title = _filename_regex_groups[3]
        _recording_type = _filename_regex_groups[4]
        _recording_duration = audio.info.length  # duration in seconds

        return {
            "file": _filename,
            "name": _recording_name,
            "title": _recording_title,
            "kind": _recording_kind,
            "date": _recording_date,
            "type": _recording_type,
            "duration": float(_recording_duration),
        }
    except Exception as e:
        logger.warning(f"encountered error for {recording_file_path}: {e}")
        return None


def identify_date_gaps(
    df: pd.DataFrame, date_column: str = "date", threshold: timedelta = timedelta(days=1)
) -> pd.DataFrame:
    """
    Identifies gaps in datetime data that exceed a specified threshold.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing datetime data
    date_column : str
        Name of the column containing datetime data
    threshold : timedelta
        The minimum gap size to report

    Returns
    -------
    pd.DataFrame
        A dataframe containing the gaps found, with columns for start_date,
        end_date, and gap_days
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])

    df = df.sort_values(by=date_column).reset_index(drop=True)

    gaps = []
    for i in range(1, len(df)):
        current_date = df[date_column].iloc[i]
        previous_date = df[date_column].iloc[i - 1]
        gap = current_date - previous_date

        if gap > threshold:
            gaps.append(
                {
                    "start_date": previous_date,
                    "end_date": current_date,
                    "gap_days": gap.total_seconds() / (60 * 60 * 24) - 1,
                }
            )

    if gaps:
        return pd.DataFrame(gaps)
    else:
        return pd.DataFrame(columns=["start_date", "end_date", "gap_days"])


def analyze_and_print_gaps(df: pd.DataFrame, min_gap_days: int = 1) -> None:
    """Analyze and print temporal discontinuities in the data."""
    print("Analyzing temporal data for discontinuities...")

    gaps_df = identify_date_gaps(df, threshold=timedelta(days=min_gap_days + 1))

    if len(gaps_df) > 0:
        print(f"Located {len(gaps_df)} temporal discontinuities exceeding {min_gap_days} days:")
        print("=" * 60)

        for i, (_, row) in enumerate(gaps_df.iterrows()):
            print(f"Gap {i + 1}:")
            print(f"  Start: {row['start_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  End:   {row['end_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duration: {row['gap_days']:.2f} days")
            print("-" * 60)

        print("\nSummary:")
        print(f"  Total gaps found: {len(gaps_df)}")
        print(f"  Average gap size: {gaps_df['gap_days'].mean():.2f} days")
        print(f"  Maximum gap size: {gaps_df['gap_days'].max():.2f} days")
        print(f"  Minimum gap size: {gaps_df['gap_days'].min():.2f} days")
    else:
        print("No temporal discontinuities detected. Data integrity confirmed.")


def plot_recordings_stats(df: pd.DataFrame) -> None:
    """Plot recording statistics with duration and weekly counts."""
    # STAGE 1 - analyse the stats
    total_duration_s = df["duration"].sum()
    total_duration_h = total_duration_s / 3600
    total_duration_d = np.floor(total_duration_h / 24)
    total_duration_d_h = total_duration_h - total_duration_d * 24
    date_min = df["date"].min()
    date_max = df["date"].max()

    # Duration by date with rolling average
    df_duration_by_date = df.groupby("date")["duration"].sum() / 60
    df_duration_by_date = (
        df_duration_by_date.to_frame()["duration"]
        .to_frame()
        .rolling(14, closed="both", center=True)
        .mean()
    )
    df_duration_by_date = df_duration_by_date.bfill().ffill()

    # Count by week
    df_count_by_week = df.copy()
    df_count_by_week["week"] = (
        df["date"].dt.strftime("%Y") + "-" + df["date"].dt.strftime("%W")
    )
    df_count_by_week = df_count_by_week.groupby("week").agg({"date": ["min"], "name": ["count"]})
    df_count_by_week = (
        df_count_by_week.droplevel(axis=1, level=1)
        .rename(columns={"name": "count"})
        .reset_index()
        .set_index("date")
        .drop("week", axis=1)
    )
    df_count_by_week.iloc[[0, -1], [0]] = None
    df_count_by_week = (
        df_count_by_week["count"].to_frame().rolling(1, closed="both", center=True).mean()
    )
    df_count_by_week = df_count_by_week.bfill().ffill()
    df_count_by_week["count"] = df_count_by_week["count"].round()

    # STAGE 2 - plot the results
    year_colors = {
        2021: "#1f77a4",
        2022: "#5ca05c",
        2023: "#d65758",
        2024: "#9477bd",
        2025: "#ff7f0e",
    }

    df_duration_by_date["year"] = df_duration_by_date.index.year

    fig, axs = plt.subplots(2, 1, figsize=(12, 8))

    # FIRST PLOT: Duration data colored by year
    years = sorted(df_duration_by_date.index.year.unique())
    for year in years:
        year_data = df_duration_by_date[df_duration_by_date.index.year == year]
        color = year_colors.get(year, "blue")

        axs[0].scatter(
            year_data.index,
            year_data["duration"],
            linewidth=0.05,
            s=25,
            alpha=1,
            color=color,
            label=str(year),
        )
        axs[0].vlines(
            x=year_data.index, ymin=0, ymax=year_data["duration"], color=color, alpha=0.8
        )

    axs[0].set_title(
        f"Recordings duration from {date_min.date()} to {date_max.date()}\n"
        f"Total: {total_duration_h:,.0f} hours ({total_duration_d:,.0f} days and {total_duration_d_h:.0f} hours), {len(df)} recordings"
    )
    axs[0].grid(axis="y")
    axs[0].set_ylabel("Duration (minutes)")
    axs[0].set_xlabel("Date")
    axs[0].set_xlim((date_min, date_max))
    axs[0].set_ylim(bottom=0)
    axs[0].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))
    axs[0].tick_params(axis="x", labelrotation=45, labelsize=8)

    legend_elements = [
        Line2D([0], [0], color=year_colors.get(year, "black"), lw=4, label=str(year))
        for year in years
    ]
    axs[0].legend(handles=legend_elements, loc="lower right", title="Years")

    # SECOND PLOT: Weekly count data colored by year
    df_count_by_week["year"] = df_count_by_week.index.year
    x_positions = mdates.date2num(df_count_by_week.index)

    if len(x_positions) > 1:
        avg_spacing = np.mean(np.diff(x_positions))
        width = avg_spacing * 0.98
    else:
        width = 7

    min_date = min(df_count_by_week.index)
    max_date = max(df_count_by_week.index)
    half_width_days = width / 2

    for i, (idx, row) in enumerate(df_count_by_week.iterrows()):
        if not np.isnan(row["count"]):
            year = idx.year
            color = year_colors.get(year, "blue")
            axs[1].bar(
                x_positions[i],
                row["count"],
                width=width,
                color=color,
                alpha=0.9,
                edgecolor="black",
                linewidth=0.5,
            )

    axs[1].set_title(f"Weekly recording count over {len(df_count_by_week)} weeks")
    axs[1].grid(axis="y")
    axs[1].set_ylabel("Recordings per week")
    axs[1].set_xlabel("Week")

    left_limit = mdates.date2num(min_date) - half_width_days
    right_limit = mdates.date2num(max_date) + half_width_days
    axs[1].set_xlim(left_limit, right_limit)

    axs[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axs[1].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))
    axs[1].tick_params(axis="x", labelrotation=45, labelsize=8)

    axs[1].legend(handles=legend_elements, loc="lower right", title="Years")
    axs[1].autoscale(enable=False)

    plt.rcParams["axes.xmargin"] = 0
    fig.tight_layout(rect=[0, 0.01, 1, 0.99])
    plt.show()


# EOF
