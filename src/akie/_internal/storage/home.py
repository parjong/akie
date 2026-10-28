"""Open an akie home: check its manifest and pick the storage engine."""

from collections.abc import Callable
from pathlib import Path

from akie._internal.core.errors import ManifestError
from akie._internal.storage import fs, manifest
from akie._internal.storage.engine import StorageEngine
from akie._internal.storage.local import LocalStorageEngine

_ENGINES: dict[str, Callable[[Path], StorageEngine]] = {
    "local": LocalStorageEngine,
}
_DEFAULT_ENGINE = "local"


def _engine_for(home: Path, found: manifest.Manifest) -> StorageEngine:
    factory = _ENGINES.get(found.storage_engine)
    if factory is None:
        raise ManifestError(
            f"{manifest.path_in(home)}: unsupported storage engine "
            f"{found.storage_engine!r}"
        )
    return factory(home)


def open_existing(home: Path) -> StorageEngine | None:
    """Return the engine of an initialized home, or ``None`` if it has no manifest.

    Reading never creates anything.
    """
    found = manifest.read(home)
    return None if found is None else _engine_for(home, found)


def initialize(home: Path) -> StorageEngine:
    """Return the engine, creating the home and its manifest on first use.

    Refuses to adopt a directory that already has other content but no manifest.
    """
    engine = open_existing(home)
    if engine is not None:
        return engine

    if home.exists():
        if not home.is_dir() or any(home.iterdir()):
            raise ManifestError(
                f"{home} exists but has no {manifest.FILENAME}; "
                "refusing to use it as an akie home"
            )
    else:
        home.parent.mkdir(parents=True, exist_ok=True)
        fs.ensure_dir(home)

    try:
        manifest.create(home, manifest.Manifest(storage_engine=_DEFAULT_ENGINE))
    except FileExistsError:
        pass  # another process initialized it first
    engine = open_existing(home)
    if engine is None:
        raise ManifestError(f"failed to create {manifest.path_in(home)}")
    return engine
