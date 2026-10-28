"""What ``add`` does when the key already exists."""

from enum import Enum


class OnDuplicate(Enum):
    ERROR = "error"
    """Raise ``KeyExists`` (default)."""

    IGNORE = "ignore"
    """Do nothing and succeed. The stored value is left untouched."""

    OVERWRITE = "overwrite"
    """Replace the stored value."""
