import stat
from pathlib import Path

import pytest

from akie import (
    AkieError,
    InvalidKeyName,
    KeyExists,
    KeyNotFound,
    KeyStore,
    OnDuplicate,
)


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "akie"
    monkeypatch.setenv("AKIE_HOME", str(path))
    return path


def test_add_then_get(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "sk-123")
    assert keys.get("google/work") == "sk-123"


def test_a_new_instance_sees_what_another_stored(home: Path) -> None:
    KeyStore().add("google/work", "sk-123")
    assert KeyStore().get("google/work") == "sk-123"


def test_duplicate_is_an_error_by_default(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "old")
    with pytest.raises(KeyExists):
        keys.add("google/work", "new")
    assert keys.get("google/work") == "old"


def test_ignore_keeps_the_old_value_and_succeeds(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "old")
    keys.add("google/work", "new", on_duplicate=OnDuplicate.IGNORE)
    assert keys.get("google/work") == "old"


def test_ignore_still_stores_a_new_key(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "value", on_duplicate=OnDuplicate.IGNORE)
    assert keys.get("google/work") == "value"


def test_overwrite_replaces_the_value(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "old")
    keys.add("google/work", "new", on_duplicate=OnDuplicate.OVERWRITE)
    assert keys.get("google/work") == "new"


def test_overwrite_stores_a_new_key(home: Path) -> None:
    keys = KeyStore()
    keys.add("google/work", "value", on_duplicate=OnDuplicate.OVERWRITE)
    assert keys.get("google/work") == "value"


def test_invalid_name_is_rejected_before_touching_the_disk(home: Path) -> None:
    with pytest.raises(InvalidKeyName):
        KeyStore().add("Google/Work", "x")
    with pytest.raises(InvalidKeyName):
        KeyStore().get("nodomain")
    assert not home.exists()


def test_on_duplicate_must_be_the_enum_not_a_string(home: Path) -> None:
    with pytest.raises(TypeError):
        KeyStore().add("a/b", "x", on_duplicate="ignore")  # type: ignore[arg-type]
    assert not home.exists()


def test_value_must_be_str(home: Path) -> None:
    with pytest.raises(TypeError):
        KeyStore().add("a/b", b"x")  # type: ignore[arg-type]


def test_get_missing_key_in_an_initialized_home(home: Path) -> None:
    keys = KeyStore()
    keys.add("a/b", "x")
    with pytest.raises(KeyNotFound):
        keys.get("a/c")


def test_get_on_a_fresh_home_is_an_error_and_creates_nothing(home: Path) -> None:
    with pytest.raises(AkieError, match="not an akie home"):
        KeyStore().get("a/b")
    assert not home.exists()


def test_constructing_a_store_creates_nothing(home: Path) -> None:
    KeyStore()
    assert not home.exists()


def test_get_notices_a_home_initialized_after_construction(home: Path) -> None:
    early = KeyStore()
    KeyStore().add("a/b", "x")
    assert early.get("a/b") == "x"


def test_first_add_creates_home_manifest_and_strict_permissions(home: Path) -> None:
    KeyStore().add("google/work", "sk-123")
    assert (home / "manifest.toml").read_text() == (
        'version = 1\nstorage_engine = "local"\n'
    )
    assert stat.S_IMODE(home.stat().st_mode) == 0o700
    assert stat.S_IMODE((home / "keys" / "google" / "work").stat().st_mode) == 0o600


def test_default_location_follows_xdg_data_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    KeyStore().add("a/b", "x")
    assert (tmp_path / "xdg" / "akie" / "manifest.toml").is_file()


def test_a_directory_with_other_content_is_not_adopted(home: Path) -> None:
    home.mkdir()
    (home / "stranger").write_text("x")
    with pytest.raises(AkieError, match="refusing"):
        KeyStore().add("a/b", "x")


def test_an_invalid_manifest_fails_at_construction(home: Path) -> None:
    home.mkdir()
    (home / "manifest.toml").write_text('version = 1\nstorage_engine = "s3"\n')
    with pytest.raises(AkieError, match="unsupported storage engine"):
        KeyStore()
