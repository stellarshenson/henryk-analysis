# Migration Checklist

Comparison between old (`henryk-analysis/`) and new (`henryk-analysis/henryk-analysis/`) project structures.

## Critical - Code Migration

- [x] **visualization/visualize.py** - Migrated to `plots.py` with all visualization functions
- [x] **recordings/** - All 3 modules migrated (`recordings.py`, `transcriptions.py`, `classification.py`)
- [x] **config.py** - Updated with pathlib-based paths
- [x] **logger.py** - Migrated with colorama and loguru support
- [x] **utils.py** - Migrated utility functions

## Notebooks

- [x] **notebooks/recordings/** - 8 notebooks copied with updated imports
- [x] **notebooks/visits/** - 3 notebooks copied (no lib imports needed)

## Resources and Data

- [x] **data/processed/** - All parquet files migrated
- [x] **resources/** - All JSON mappings and templates migrated
- [x] **.res/** - README images copied
- [x] **references/@attachments/** - Chart images copied
- [x] **reports/*.pdf** - Generated report copied

## Configuration

- [x] **.env.template** - Environment template copied
- [x] **pyproject.toml** - Updated with all dependencies
- [x] **.claude/** - Migrated with updated CLAUDE.md

## Library Modules

- [x] **lib_henryk_analysis/dataset.py** - Updated with data loading utilities
- [x] **lib_henryk_analysis/plots.py** - Full visualization code migrated
- [x] **lib_henryk_analysis/features.py** - Stub (old was empty)
- [x] **lib_henryk_analysis/modeling/** - Stubs (old were empty)

## Structure Comparison

| Old Structure | New Structure | Status |
|---------------|---------------|--------|
| `src/lib_henryk/` | `lib_henryk_analysis/` | COMPLETE |
| `src/lib_henryk/recordings/` | `lib_henryk_analysis/recordings/` | COMPLETE |
| `src/lib_henryk/visualization/` | `lib_henryk_analysis/plots.py` | COMPLETE |
| `src/lib_henryk/data/` | `lib_henryk_analysis/dataset.py` | COMPLETE |
| `environment.yml` | `pyproject.toml` | COMPLETE |
| `notebooks/` | `notebooks/` | COMPLETE |
| `.res/` | `.res/` | COMPLETE |

## New Features (From Template)

- [x] `docs/` - mkdocs documentation structure
- [x] `tests/` - Test directory
- [x] `data/raw/`, `data/interim/`, `data/external/` - Structured data directories
- [x] `reports/figures/` - Figures subdirectory
- [x] `ruff` linting configuration
- [x] Modern `pyproject.toml` with optional dependencies

## Migration Complete

All items have been addressed. The new project structure is ready for use:

```bash
cd henryk-analysis
pip install -e ".[dev]"
```

**Key Changes:**
- Python 3.12 (was 3.11)
- Module renamed `lib_henryk` -> `lib_henryk_analysis`
- pathlib-based paths throughout
- loguru logging (was custom ColoredFormatter)
- Modern pyproject.toml (abandoned environment.yml)
- ruff linting, mkdocs documentation
