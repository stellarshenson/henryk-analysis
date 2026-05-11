"""
lib_henryk_analysis - Henryk content creation and analysis library.

A library for processing audio recordings, transcriptions, and classifications
for the Henry Project "Hope" - AI Analysis and Generation.
"""
from lib_henryk_analysis import config  # noqa: F401
from lib_henryk_analysis import logger  # noqa: F401
from lib_henryk_analysis import utils  # noqa: F401
from lib_henryk_analysis.config import (
    DATA_DIR,
    FIGURES_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    PROJ_ROOT,
    REPORTS_DIR,
    RESOURCES_DIR,
)

__version__ = "0.6.84"

__all__ = [
    "config",
    "logger",
    "utils",
    "PROJ_ROOT",
    "DATA_DIR",
    "PROCESSED_DATA_DIR",
    "MODELS_DIR",
    "REPORTS_DIR",
    "FIGURES_DIR",
    "RESOURCES_DIR",
]

# EOF
