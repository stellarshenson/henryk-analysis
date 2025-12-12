<!-- Import workspace-level CLAUDE.md configuration -->
<!-- See /home/lab/workspace/.claude/CLAUDE.md for complete rules -->

# Project-Specific Configuration

This file extends workspace-level configuration with project-specific rules.

## Project Context

**Project**: Henry Project "Hope" - AI Analysis and Generation
**Purpose**: Process 700+ audio recordings (approximately 200 hours) made for an alienated son, Henry. Extract information, generate transcriptions, classifications, and prepare content for delivery through various channels.

**Library**: `lib_henryk_analysis` (v0.1.0)
**Conda Environment**: `henryk`
**Python Version**: 3.12

## Project Structure

```
henryk-analysis/
├── lib_henryk_analysis/     # Main library
│   ├── recordings/          # Recording processing (transcriptions, classification)
│   │   ├── recordings.py    # File discovery, metadata extraction, plotting
│   │   ├── transcriptions.py # Transcription processing via GoodTape API
│   │   └── classification.py # OpenAI GPT classification
│   ├── config.py            # Configuration and paths
│   ├── logger.py            # Logging utilities, progress bars, colored output
│   ├── utils.py             # General utilities
│   ├── dataset.py           # Dataset generation
│   ├── features.py          # Feature engineering
│   ├── plots.py             # Visualization
│   └── modeling/            # ML models (train/predict)
├── notebooks/
│   └── recordings/          # Jupyter notebooks for recordings analysis
├── data/
│   ├── raw/                 # Raw data
│   ├── interim/             # Intermediate data
│   ├── processed/           # Processed parquet files
│   └── external/            # External data
├── resources/               # Templates and prompts
├── references/              # Reference documentation
├── models/                  # Trained models
├── reports/
│   └── figures/             # Generated figures
├── docs/                    # Documentation (mkdocs)
└── tests/                   # Tests
```

## Key Data Files

- `henryk_recordings_stats.parquet` - Recording statistics
- `henryk_recordings_transcriptions.parquet.zip` - Transcriptions (compressed)
- `henryk_transcriptions_classifications.parquet` - NLP classifications
- `henryk_transcriptions_classifications_stats.parquet` - Classification statistics

## Notebook Pipeline

1. Generate recordings stats
2. Analyse recordings stats
3. Transcribe recordings
4. Generate recordings descriptions
5. Analyse transcription classifications
6. Generate images for recordings
7. Generate videos from recordings

## Running Commands

All Python commands should use the `henryk` conda environment:
```bash
conda run --name henryk python script.py
```

Or install with pip:
```bash
pip install -e ".[dev]"
```

## Technology Stack

- **Data Processing**: pandas, polars, pyarrow, numpy
- **AI/NLP**: OpenAI API, transformers, json_repair
- **Audio**: pydub, ffmpeg-binaries
- **Visualization**: matplotlib, seaborn, plotly, wordcloud
- **Document Generation**: python-docx, markdown-it-py
- **Logging**: loguru, colorama
- **CLI**: typer, click
- **Development**: ruff, pytest, mkdocs

## Module Imports

```python
# Import the library
import lib_henryk_analysis as hk
from lib_henryk_analysis.config import PROCESSED_DATA_DIR, PROJ_ROOT
from lib_henryk_analysis.logger import logger, progress_bar, coloured_print

# Import recordings submodules
from lib_henryk_analysis.recordings import recordings
from lib_henryk_analysis.recordings import transcriptions
from lib_henryk_analysis.recordings.classification import TranscriptionClassifier
```

## Sensitive Content Notes

- Audio recordings and transcriptions are encrypted pending legal review
- Classification datasets are available in `data/processed`
- Content serves both therapeutic and legal (parental alienation case) purposes
