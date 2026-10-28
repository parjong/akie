"""Where the akie home lives."""

from collections.abc import Mapping
from pathlib import Path

from akie._internal.core.errors import HomeError


def resolve_home(environ: Mapping[str, str]) -> Path:
    """``$AKIE_HOME``, else ``${XDG_DATA_HOME:-~/.local/share}/akie``.

    Empty values count as unset. A relative ``AKIE_HOME`` is an error because
    its meaning would depend on the current directory. A relative
    ``XDG_DATA_HOME`` is ignored, as the XDG specification requires.
    """
    akie_home = environ.get("AKIE_HOME")
    if akie_home:
        path = Path(akie_home)
        if not path.is_absolute():
            raise HomeError(f"AKIE_HOME must be an absolute path, got {akie_home!r}")
        return path

    xdg_data_home = environ.get("XDG_DATA_HOME")
    if xdg_data_home and Path(xdg_data_home).is_absolute():
        data_home = Path(xdg_data_home)
    else:
        data_home = Path.home() / ".local" / "share"
    return data_home / "akie"
