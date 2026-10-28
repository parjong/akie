"""Key names: ``<domain>/<slug>``."""

import re
from dataclasses import dataclass

from akie._internal.core.errors import InvalidKeyName

# Lowercase only so that names never collide on case-insensitive file systems.
# The first character must be alphanumeric so a name can never be ``..`` or a
# hidden file, which also keeps names clear of our ``.tmp-*`` scratch files.
_PART = r"[a-z0-9][a-z0-9._-]{0,63}"
_NAME = re.compile(rf"({_PART})/({_PART})")


@dataclass(frozen=True)
class KeyName:
    domain: str
    slug: str

    @classmethod
    def parse(cls, text: str) -> "KeyName":
        if not isinstance(text, str):
            raise TypeError(f"key name must be str, not {type(text).__name__}")
        match = _NAME.fullmatch(text)
        if match is None:
            raise InvalidKeyName(
                f"invalid key name {text!r}: expected <domain>/<slug>, each part "
                "1-64 characters of [a-z0-9._-] starting with [a-z0-9]"
            )
        return cls(domain=match.group(1), slug=match.group(2))

    def __str__(self) -> str:
        return f"{self.domain}/{self.slug}"
