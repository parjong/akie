"""akie: a small local store for API keys.

Everything importable from here is the public API. Anything under
``akie._internal`` may change at any time.
"""

from akie._internal.core.duplicate import OnDuplicate
from akie._internal.core.errors import (
    AkieError,
    InvalidKeyName,
    KeyExists,
    KeyNotFound,
)
from akie._internal.service.key_store import KeyStore

__all__ = [
    "AkieError",
    "InvalidKeyName",
    "KeyExists",
    "KeyNotFound",
    "KeyStore",
    "OnDuplicate",
]
