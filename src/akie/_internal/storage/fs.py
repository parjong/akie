"""Small filesystem helpers that enforce akie's permissions.

Directories are created ``700`` and files ``600``. The process umask can only
make these stricter, never looser.
"""

import os
import tempfile
from pathlib import Path

DIR_MODE = 0o700
FILE_MODE = 0o600
SCRATCH_PREFIX = ".tmp-"


def ensure_dir(path: Path) -> None:
    """Create one directory level (the parent must exist). Existing is fine."""
    try:
        path.mkdir(mode=DIR_MODE)
    except FileExistsError:
        if not path.is_dir():
            raise


def create_exclusive(path: Path, data: bytes) -> None:
    """Create ``path`` with ``data``; raise ``FileExistsError`` if it exists."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
    except BaseException:
        # We created the file, so remove the partial result.
        path.unlink(missing_ok=True)
        raise


def replace_atomic(path: Path, data: bytes) -> None:
    """Write ``data`` to ``path`` so readers see either the old or the new value."""
    fd, scratch = tempfile.mkstemp(dir=path.parent, prefix=SCRATCH_PREFIX)
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
        os.replace(scratch, path)
    except BaseException:
        Path(scratch).unlink(missing_ok=True)
        raise
