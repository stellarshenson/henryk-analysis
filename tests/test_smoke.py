"""Import smoke tests + version consistency check."""
import tomllib
from pathlib import Path


def test_package_imports():
    import henryk_analysis

    assert henryk_analysis is not None
    assert hasattr(henryk_analysis, "__version__")


def test_version_matches_pyproject(project_root: Path):
    import henryk_analysis

    pyproject = project_root / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    assert henryk_analysis.__version__ == data["project"]["version"]


def test_top_level_submodules_import():
    from henryk_analysis import config, logger, utils  # noqa: F401


def test_recordings_submodules_import():
    from henryk_analysis.recordings import (  # noqa: F401
        classification,
        recordings,
        transcriptions,
    )


def test_extras_import():
    from henryk_analysis import dataset, features, plots  # noqa: F401
    from henryk_analysis.modeling import predict, train  # noqa: F401


def test_public_api_re_exports():
    import henryk_analysis as hk

    for name in (
        "PROJ_ROOT",
        "DATA_DIR",
        "PROCESSED_DATA_DIR",
        "MODELS_DIR",
        "REPORTS_DIR",
        "FIGURES_DIR",
        "RESOURCES_DIR",
    ):
        assert hasattr(hk, name), f"henryk_analysis.{name} missing"
