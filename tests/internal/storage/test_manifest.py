from pathlib import Path

import pytest

from akie._internal.core.errors import ManifestError
from akie._internal.storage import manifest


def write(home: Path, text: str) -> None:
    (home / manifest.FILENAME).write_text(text, encoding="utf-8")


def test_read_returns_none_without_a_manifest(tmp_path: Path) -> None:
    assert manifest.read(tmp_path) is None


def test_create_then_read_round_trips(tmp_path: Path) -> None:
    manifest.create(tmp_path, manifest.Manifest(storage_engine="local"))
    assert manifest.read(tmp_path) == manifest.Manifest("local", 1)


def test_create_refuses_to_replace_an_existing_manifest(tmp_path: Path) -> None:
    manifest.create(tmp_path, manifest.Manifest(storage_engine="local"))
    with pytest.raises(FileExistsError):
        manifest.create(tmp_path, manifest.Manifest(storage_engine="local"))


def test_dumps_is_the_documented_format() -> None:
    text = manifest.Manifest(storage_engine="local").dumps()
    assert text == 'version = 1\nstorage_engine = "local"\n'


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("not toml [", "not valid TOML"),
        ('version = 1\nstorage_engine = "local"\nextra = 1\n', "unknown keys: extra"),
        ('storage_engine = "local"\n', "missing keys: version"),
        ("version = 1\n", "missing keys: storage_engine"),
        ('version = 2\nstorage_engine = "local"\n', "unsupported version 2"),
        ('version = true\nstorage_engine = "local"\n', "unsupported version"),
        ('version = "1"\nstorage_engine = "local"\n', "unsupported version"),
        ("version = 1\nstorage_engine = 3\n", "must be a string"),
    ],
)
def test_read_rejects_invalid_manifests(
    tmp_path: Path, text: str, fragment: str
) -> None:
    write(tmp_path, text)
    with pytest.raises(ManifestError, match=fragment):
        manifest.read(tmp_path)
