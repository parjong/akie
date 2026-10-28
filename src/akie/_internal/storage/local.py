"""The ``local`` storage engine: one file per key under ``<home>/keys``.

.. code-block:: text

    <home>/keys/<domain>/<slug>    # the value, verbatim, mode 600
"""

from pathlib import Path

from akie._internal.core.errors import KeyExists, KeyNotFound
from akie._internal.core.name import KeyName
from akie._internal.storage import fs


class LocalStorageEngine:
    def __init__(self, home: Path) -> None:
        self._keys_dir = home / "keys"

    def read(self, name: KeyName) -> str:
        try:
            return self._path(name).read_bytes().decode("utf-8")
        except FileNotFoundError:
            raise KeyNotFound(f"no such key: {name}") from None

    def create(self, name: KeyName, value: str) -> None:
        path = self._prepare(name)
        try:
            fs.create_exclusive(path, value.encode("utf-8"))
        except FileExistsError:
            raise KeyExists(f"key already exists: {name}") from None

    def replace(self, name: KeyName, value: str) -> None:
        fs.replace_atomic(self._prepare(name), value.encode("utf-8"))

    def _path(self, name: KeyName) -> Path:
        return self._keys_dir / name.domain / name.slug

    def _prepare(self, name: KeyName) -> Path:
        """Create the directories a key needs and return its file path."""
        fs.ensure_dir(self._keys_dir)
        fs.ensure_dir(self._keys_dir / name.domain)
        return self._path(name)
