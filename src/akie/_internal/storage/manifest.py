"""``manifest.toml``: records which storage engine owns an akie home.

.. code-block:: toml

    version = 1
    storage_engine = "local"
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from akie._internal.core.errors import ManifestError
from akie._internal.storage import fs

FILENAME = "manifest.toml"
SUPPORTED_VERSION = 1
_KEYS = {"version", "storage_engine"}


@dataclass(frozen=True)
class Manifest:
    storage_engine: str
    version: int = SUPPORTED_VERSION

    def dumps(self) -> str:
        return f'version = {self.version}\nstorage_engine = "{self.storage_engine}"\n'


def path_in(home: Path) -> Path:
    return home / FILENAME


def read(home: Path) -> Manifest | None:
    """Return the validated manifest, or ``None`` if the home has none."""
    path = path_in(home)
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ManifestError(f"{path} is not valid TOML: {error}") from error

    unknown = sorted(set(data) - _KEYS)
    if unknown:
        raise ManifestError(f"{path} has unknown keys: {', '.join(unknown)}")
    missing = sorted(_KEYS - set(data))
    if missing:
        raise ManifestError(f"{path} is missing keys: {', '.join(missing)}")

    version = data["version"]
    if type(version) is not int or version != SUPPORTED_VERSION:
        raise ManifestError(f"{path} has unsupported version {version!r}")
    storage_engine = data["storage_engine"]
    if not isinstance(storage_engine, str):
        raise ManifestError(f"{path}: storage_engine must be a string")
    return Manifest(storage_engine=storage_engine, version=version)


def create(home: Path, manifest: Manifest) -> None:
    """Write the manifest; raise ``FileExistsError`` if one already exists."""
    fs.create_exclusive(path_in(home), manifest.dumps().encode("utf-8"))
