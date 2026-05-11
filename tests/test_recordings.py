"""Tests for henryk_analysis.recordings - audio file processing."""
from datetime import datetime
from pathlib import Path

FIXTURE_M4A = (
    Path(__file__).parent
    / "fixtures"
    / "Henryk 2026-01-14 Tatuś opowiada o tym jak się robi filmy.m4a"
)


def test_get_audio_file_info_m4a_fixture():
    """Process the bundled m4a fixture and verify all metadata fields."""
    from henryk_analysis.recordings.recordings import get_audio_file_info

    assert FIXTURE_M4A.exists(), f"fixture missing: {FIXTURE_M4A}"

    info = get_audio_file_info(str(FIXTURE_M4A))

    assert info is not None, "mutagen failed to read the m4a fixture"

    assert info["file"] == FIXTURE_M4A.name
    assert info["name"] == FIXTURE_M4A.stem
    assert info["kind"] == "Henryk"
    assert info["date"] == datetime(2026, 1, 14)
    assert info["title"] == "Tatuś opowiada o tym jak się robi filmy"
    assert info["type"] == "m4a"

    assert isinstance(info["duration"], float)
    assert info["duration"] > 0, "m4a duration should be positive"


def test_get_audio_file_info_returns_none_for_unreadable_file(tmp_path: Path):
    """Mutagen returns None for non-audio files; function surfaces that as None."""
    from henryk_analysis.recordings.recordings import get_audio_file_info

    fake = tmp_path / "Henryk 2026-01-14 not-real.m4a"
    fake.write_bytes(b"not a real m4a")

    assert get_audio_file_info(str(fake)) is None


def test_get_audio_file_info_returns_none_for_unparseable_filename(tmp_path: Path):
    """Filename must match `<kind> <YYYY-MM-DD> <title>.<ext>` or function returns None."""
    from henryk_analysis.recordings.recordings import get_audio_file_info

    bad_name = tmp_path / "wrong-pattern.m4a"
    bad_name.write_bytes(b"x")

    assert get_audio_file_info(str(bad_name)) is None
