from pathlib import Path

import pytest

from akie._internal.core.errors import HomeError
from akie._internal.core.paths import resolve_home


def test_akie_home_wins() -> None:
    env = {"AKIE_HOME": "/srv/akie", "XDG_DATA_HOME": "/xdg"}
    assert resolve_home(env) == Path("/srv/akie")


def test_xdg_data_home_is_used_when_akie_home_is_unset() -> None:
    assert resolve_home({"XDG_DATA_HOME": "/xdg"}) == Path("/xdg/akie")


def test_default_is_under_local_share(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", "/home/someone")
    assert resolve_home({}) == Path("/home/someone/.local/share/akie")


def test_empty_values_count_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", "/home/someone")
    env = {"AKIE_HOME": "", "XDG_DATA_HOME": ""}
    assert resolve_home(env) == Path("/home/someone/.local/share/akie")


def test_relative_xdg_data_home_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", "/home/someone")
    expected = Path("/home/someone/.local/share/akie")
    assert resolve_home({"XDG_DATA_HOME": "relative"}) == expected


def test_relative_akie_home_is_an_error() -> None:
    with pytest.raises(HomeError):
        resolve_home({"AKIE_HOME": "relative/dir"})
