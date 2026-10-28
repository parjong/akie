"""The contract a storage engine fulfils. Internal, not part of the public API.

An engine only offers primitive operations. The duplicate policy
(``OnDuplicate``) is decided by the service layer on top of them.
"""

from typing import Protocol

from akie._internal.core.name import KeyName


class StorageEngine(Protocol):
    def read(self, name: KeyName) -> str:
        """Return the stored value; raise ``KeyNotFound`` if there is none."""
        ...

    def create(self, name: KeyName, value: str) -> None:
        """Store a new value; raise ``KeyExists`` if the key already exists."""
        ...

    def replace(self, name: KeyName, value: str) -> None:
        """Store ``value``, replacing any existing one. Readers never see a mix."""
        ...
