<!-- @import /home/lab/workspace/.claude/CLAUDE.md -->

# Project-Specific Configuration

This file imports workspace-level configuration from `/home/lab/workspace/.claude/CLAUDE.md`.
All workspace rules apply. Project-specific rules below strengthen or extend them.

The workspace `/home/lab/workspace/.claude/` directory contains additional instruction files
(MERMAID.md, NOTEBOOK.md, DATASCIENCE.md, GIT.md, and others) referenced by CLAUDE.md.
Consult workspace CLAUDE.md and the .claude directory to discover all applicable standards.

## Mandatory Bans (Reinforced)

The following workspace rules are STRICTLY ENFORCED for this project:

- **No automatic git tags** - only create tags when user explicitly requests
- **No automatic version changes** - only modify version in package.json/pyproject.toml/etc. when user explicitly requests
- **No automatic publishing** - never run `make publish`, `npm publish`, `twine upload`, or similar without explicit user request
- **No manual package installs if Makefile exists** - use `make install` or equivalent Makefile targets, not direct `pip install`/`uv install`/`npm install`
- **No automatic git commits or pushes** - only when user explicitly requests

## Journal Rules (Project-Specific)

- **APPEND ONLY**: New journal entries MUST be appended at the end of the file, never inserted between existing entries
- Entries maintain strict chronological order by position - the last entry in the file is always the most recent work
- Never reorder, move, or insert entries out of sequence
- The Stellars **journal plugin** is the canonical tool for this file: create via `/journal:create`, append via `/journal:update`, archive via `/journal:archive`. The `journal:journal` skill auto-triggers on any mention of "journal" and runs `journal-tools check` after every write
- Direct edits to `JOURNAL.md` are a last resort - prefer the plugin so modus secundis format, continuous numbering and append-only order are enforced automatically

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
