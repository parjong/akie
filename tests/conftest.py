import pytest


@pytest.fixture(autouse=True)
def isolated_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Never let a test see or touch the real home directory or akie home."""
    monkeypatch.setenv("HOME", str(tmp_path_factory.mktemp("home")))
    monkeypatch.delenv("AKIE_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
