"""End-to-end execution of notebook 02 (analyse recordings stats) against the
committed parquet fixture (`data/processed/henryk_recordings_stats.parquet`).

The notebook reads the parquet, plots stats, runs gap analysis, and writes a
markdown list of recording names to its working directory. We execute it
headlessly with nbclient in a tmp cwd and assert the markdown side-effect.
"""
import shutil
from pathlib import Path

import nbformat
from nbclient import NotebookClient

NOTEBOOK_PATH = (
    Path(__file__).parent.parent
    / "notebooks"
    / "recordings"
    / "02-analyse-recordings-stats.ipynb"
)


def test_notebook_02_analyse_recordings_stats(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MPLBACKEND", "Agg")

    nb_copy = tmp_path / NOTEBOOK_PATH.name
    shutil.copy(NOTEBOOK_PATH, nb_copy)

    nb = nbformat.read(nb_copy, as_version=4)
    client = NotebookClient(nb, timeout=180, kernel_name="python3")
    client.execute(cwd=str(tmp_path))

    output = tmp_path / "recording_names.md"
    assert output.exists(), "notebook did not produce recording_names.md"

    content = output.read_text(encoding="utf-8")
    assert content.startswith("# Lista nagrań")
    assert "**202" in content, "expected at least one date-prefixed entry"
