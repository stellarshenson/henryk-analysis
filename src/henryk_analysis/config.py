"""
Configuration for the henryk analysis project.

Provides path constants and environment setup.
"""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from loguru import logger

########### SETUP ###############

# Set up logger
logger.remove()
logger.add(sys.stdout, colorize=True)

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove()
    logger.add(lambda msg: tqdm.write(msg, end="", file=sys.stdout), colorize=True)
except ModuleNotFoundError:
    pass

########## VARIABLES ############

# Load environment variables from .env file if it exists
load_dotenv()

# Project root (derived from module location)
PROJ_ROOT = Path(__file__).resolve().parents[2]

# Project directories (from environment or defaults relative to PROJ_ROOT)
DATA_DIR = Path(os.getenv("DATA_DIR", PROJ_ROOT / "data"))
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", DATA_DIR / "raw"))
INTERIM_DATA_DIR = Path(os.getenv("INTERIM_DATA_DIR", DATA_DIR / "interim"))
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR", DATA_DIR / "processed"))
EXTERNAL_DATA_DIR = Path(os.getenv("EXTERNAL_DATA_DIR", DATA_DIR / "external"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", PROJ_ROOT / "models"))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", PROJ_ROOT / "reports"))
FIGURES_DIR = Path(os.getenv("FIGURES_DIR", REPORTS_DIR / "figures"))
RESOURCES_DIR = Path(os.getenv("RESOURCES_DIR", PROJ_ROOT / "resources"))

# Data files (from environment or defaults)
FILE_RECORDINGS_STATS_PARQUET = Path(
    os.getenv("FILE_RECORDINGS_STATS", PROCESSED_DATA_DIR / "henryk_recordings_stats.parquet")
)
FILE_TRANSCRIPTIONS_PARQUET = Path(
    os.getenv(
        "FILE_TRANSCRIPTIONS", PROCESSED_DATA_DIR / "henryk_recordings_transcriptions.parquet"
    )
)
FILE_TRANSCRIPTIONS_JSON = Path(
    os.getenv(
        "FILE_TRANSCRIPTIONS_JSON", PROCESSED_DATA_DIR / "henryk_recordings_transcriptions.json"
    )
)
FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET = Path(
    os.getenv(
        "FILE_CLASSIFICATIONS",
        PROCESSED_DATA_DIR / "henryk_transcriptions_classifications.parquet",
    )
)
FILE_TRANSCRIPTIONS_CLASSIFICATIONS_STATS_PARQUET = Path(
    os.getenv(
        "FILE_CLASSIFICATIONS_STATS",
        PROCESSED_DATA_DIR / "henryk_transcriptions_classifications_stats.parquet",
    )
)

# Template and prompt files (from environment or defaults)
FILE_TRANSCRIPTION_TEMPLATE = Path(
    os.getenv("FILE_TRANSCRIPTION_TEMPLATE", RESOURCES_DIR / "template_transcription.docx")
)
FILE_PROMPT_RECORDING_CLASSIFICATION = Path(
    os.getenv("FILE_PROMPT_CLASSIFICATION", RESOURCES_DIR / "prompt_recording_classification.md")
)
FILE_PROMPT_RECORDING_SUMMARY = Path(
    os.getenv("FILE_PROMPT_SUMMARY", RESOURCES_DIR / "recording_summary.md")
)

# Directories for transcriptions
DIR_TRANSCRIPTIONS = Path(os.getenv("DIR_TRANSCRIPTIONS", PROCESSED_DATA_DIR / "transcriptions"))

# External directories - recordings source location
DIR_WIADOMOSCI_DO_HENRYCZKA = Path(
    os.getenv(
        "DIR_RECORDINGS",
        "/mnt/onedrive/My Private/My documents/Other/Henryk/Alienacja rodzicielska materiały/Wiadomości do Henryczka",
    )
)
DIR_RECORDINGS = DIR_WIADOMOSCI_DO_HENRYCZKA
DIR_TRANSCRIPTIONS_DOC = Path(
    os.getenv("DIR_TRANSCRIPTIONS_DOC", DIR_WIADOMOSCI_DO_HENRYCZKA / "transkrypcje")
)

# Log current root dir
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

# EOF
