import stat
from pathlib import Path

import pytest

from akie._internal.core.errors import KeyExists, KeyNotFound
from akie._internal.core.name import KeyName
from akie._internal.storage.local import LocalStorageEngine

NAME = KeyName.parse("google/work")


def mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


@pytest.fixture
def engine(tmp_path: Path) -> LocalStorageEngine:
    return LocalStorageEngine(tmp_path)


def test_create_then_read(engine: LocalStorageEngine) -> None:
    engine.create(NAME, "sk-123")
    assert engine.read(NAME) == "sk-123"


def test_layout_is_keys_domain_slug_with_strict_modes(
    engine: LocalStorageEngine, tmp_path: Path
) -> None:
    engine.create(NAME, "sk-123")
    assert (tmp_path / "keys" / "google" / "work").read_bytes() == b"sk-123"
    assert mode(tmp_path / "keys") == 0o700
    assert mode(tmp_path / "keys" / "google") == 0o700
    assert mode(tmp_path / "keys" / "google" / "work") == 0o600


def test_value_is_stored_verbatim(engine: LocalStorageEngine) -> None:
    value = "line1\r\nline2\n  trailing  \n한글"
    engine.create(NAME, value)
    assert engine.read(NAME) == value


def test_create_refuses_duplicates_and_keeps_the_old_value(
    engine: LocalStorageEngine,
) -> None:
    engine.create(NAME, "old")
    with pytest.raises(KeyExists):
        engine.create(NAME, "new")
    assert engine.read(NAME) == "old"


def test_replace_overwrites(engine: LocalStorageEngine, tmp_path: Path) -> None:
    engine.create(NAME, "old")
    engine.replace(NAME, "new")
    assert engine.read(NAME) == "new"
    assert mode(tmp_path / "keys" / "google" / "work") == 0o600
    assert [p.name for p in (tmp_path / "keys" / "google").iterdir()] == ["work"]


def test_replace_creates_a_missing_key(engine: LocalStorageEngine) -> None:
    engine.replace(NAME, "value")
    assert engine.read(NAME) == "value"


def test_read_missing_key_raises(engine: LocalStorageEngine) -> None:
    with pytest.raises(KeyNotFound):
        engine.read(NAME)


def test_read_never_creates_anything(
    engine: LocalStorageEngine, tmp_path: Path
) -> None:
    with pytest.raises(KeyNotFound):
        engine.read(NAME)
    assert list(tmp_path.iterdir()) == []


def test_keys_in_different_domains_are_independent(
    engine: LocalStorageEngine,
) -> None:
    engine.create(KeyName.parse("a/x"), "1")
    engine.create(KeyName.parse("b/x"), "2")
    assert engine.read(KeyName.parse("a/x")) == "1"
    assert engine.read(KeyName.parse("b/x")) == "2"
