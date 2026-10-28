import stat
from pathlib import Path

import pytest

from akie._internal.storage import fs


def mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def test_ensure_dir_creates_mode_700(tmp_path: Path) -> None:
    target = tmp_path / "d"
    fs.ensure_dir(target)
    assert mode(target) == 0o700


def test_ensure_dir_accepts_existing_directory(tmp_path: Path) -> None:
    fs.ensure_dir(tmp_path)


def test_ensure_dir_rejects_a_file(tmp_path: Path) -> None:
    file = tmp_path / "f"
    file.write_text("x")
    with pytest.raises(FileExistsError):
        fs.ensure_dir(file)


def test_create_exclusive_writes_mode_600(tmp_path: Path) -> None:
    target = tmp_path / "f"
    fs.create_exclusive(target, b"secret")
    assert target.read_bytes() == b"secret"
    assert mode(target) == 0o600


def test_create_exclusive_refuses_to_replace_and_keeps_old_value(
    tmp_path: Path,
) -> None:
    target = tmp_path / "f"
    fs.create_exclusive(target, b"old")
    with pytest.raises(FileExistsError):
        fs.create_exclusive(target, b"new")
    assert target.read_bytes() == b"old"


def test_replace_atomic_creates_and_replaces(tmp_path: Path) -> None:
    target = tmp_path / "f"
    fs.replace_atomic(target, b"one")
    fs.replace_atomic(target, b"two")
    assert target.read_bytes() == b"two"
    assert mode(target) == 0o600


def test_replace_atomic_leaves_no_scratch_files(tmp_path: Path) -> None:
    fs.replace_atomic(tmp_path / "f", b"x")
    assert [p.name for p in tmp_path.iterdir()] == ["f"]


def test_replace_atomic_cleans_up_when_the_target_is_a_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "d"
    target.mkdir()
    with pytest.raises(OSError):  # noqa: PT011
        fs.replace_atomic(target, b"x")
    assert [p.name for p in tmp_path.iterdir()] == ["d"]
