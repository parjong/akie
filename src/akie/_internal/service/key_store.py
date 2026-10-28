"""``KeyStore``: the object behind ``add`` and ``get``."""

import os

from akie._internal.core.duplicate import OnDuplicate
from akie._internal.core.errors import KeyExists, ManifestError
from akie._internal.core.name import KeyName
from akie._internal.core.paths import resolve_home
from akie._internal.storage import home as akie_home
from akie._internal.storage.engine import StorageEngine


class KeyStore:
    """A local store of API keys named ``<domain>/<slug>``.

    The location comes from ``AKIE_HOME``, else
    ``${XDG_DATA_HOME:-~/.local/share}/akie``. Keys are not encrypted; they are
    protected by file permissions only (directories 700, files 600).

    Creating a ``KeyStore`` validates an existing manifest but never creates
    anything on disk. The first ``add`` creates the home.
    """

    def __init__(self) -> None:
        self._home = resolve_home(os.environ)
        self._engine: StorageEngine | None = akie_home.open_existing(self._home)

    def add(
        self,
        name: str,
        value: str,
        *,
        on_duplicate: OnDuplicate = OnDuplicate.ERROR,
    ) -> None:
        """Store ``value`` under ``name``.

        If the key already exists, ``on_duplicate`` decides: ``ERROR`` raises
        ``KeyExists``, ``IGNORE`` leaves the old value and succeeds, and
        ``OVERWRITE`` replaces it.
        """
        if not isinstance(value, str):
            raise TypeError(f"value must be str, not {type(value).__name__}")
        if not isinstance(on_duplicate, OnDuplicate):
            raise TypeError(
                "on_duplicate must be an OnDuplicate, "
                f"not {type(on_duplicate).__name__}"
            )
        key = KeyName.parse(name)

        if self._engine is None:
            self._engine = akie_home.initialize(self._home)
        engine = self._engine

        if on_duplicate is OnDuplicate.OVERWRITE:
            engine.replace(key, value)
            return
        try:
            engine.create(key, value)
        except KeyExists:
            if on_duplicate is OnDuplicate.ERROR:
                raise

    def get(self, name: str) -> str:
        """Return the value stored under ``name``. Reading creates nothing."""
        key = KeyName.parse(name)

        if self._engine is None:
            # Someone may have initialized the home since we were created.
            self._engine = akie_home.open_existing(self._home)
        if self._engine is None:
            raise ManifestError(
                f"{self._home} is not an akie home yet (no manifest.toml); "
                "add a key first"
            )
        return self._engine.read(key)
