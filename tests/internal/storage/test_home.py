import stat
from pathlib import Path

import pytest

from akie._internal.core.errors import ManifestError
from akie._internal.storage import home as home_module
from akie._internal.storage import manifest
from akie._internal.storage.local import LocalStorageEngine


def test_open_existing_is_none_for_a_missing_directory(tmp_path: Path) -> None:
    assert home_module.open_existing(tmp_path / "nope") is None
    assert not (tmp_path / "nope").exists()


def test_open_existing_is_none_for_an_empty_directory(tmp_path: Path) -> None:
    assert home_module.open_existing(tmp_path) is None
    assert list(tmp_path.iterdir()) == []


def test_initialize_creates_home_and_manifest(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "akie"
    engine = home_module.initialize(target)
    assert isinstance(engine, LocalStorageEngine)
    assert manifest.read(target) == manifest.Manifest("local", 1)
    assert stat.S_IMODE(target.stat().st_mode) == 0o700
    assert stat.S_IMODE((target / manifest.FILENAME).stat().st_mode) == 0o600


def test_initialize_adopts_an_empty_directory(tmp_path: Path) -> None:
    home_module.initialize(tmp_path)
    assert manifest.read(tmp_path) is not None


def test_initialize_is_idempotent(tmp_path: Path) -> None:
    home_module.initialize(tmp_path)
    home_module.initialize(tmp_path)
    assert manifest.read(tmp_path) == manifest.Manifest("local", 1)


def test_initialize_refuses_a_directory_with_other_content(tmp_path: Path) -> None:
    (tmp_path / "something").write_text("x")
    with pytest.raises(ManifestError, match="refusing"):
        home_module.initialize(tmp_path)
    assert not (tmp_path / manifest.FILENAME).exists()


def test_initialize_refuses_a_file(tmp_path: Path) -> None:
    file = tmp_path / "file"
    file.write_text("x")
    with pytest.raises(ManifestError, match="refusing"):
        home_module.initialize(file)


def test_unsupported_storage_engine_is_an_error(tmp_path: Path) -> None:
    manifest.create(tmp_path, manifest.Manifest(storage_engine="s3"))
    with pytest.raises(ManifestError, match="unsupported storage engine"):
        home_module.open_existing(tmp_path)
