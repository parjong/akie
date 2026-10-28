"""Run the real entry points in a subprocess, as a user would."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


def run(home: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "AKIE_HOME": str(home)}
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "akie", *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


@pytest.fixture
def home(tmp_path: Path) -> Path:
    return tmp_path / "akie"


def test_add_and_get_through_python_dash_m(home: Path) -> None:
    added = run(home, "key", "add", "google/work", stdin="sk-123\n")
    assert (added.returncode, added.stdout, added.stderr) == (0, "", "")

    got = run(home, "key", "get", "google/work")
    assert (got.returncode, got.stdout, got.stderr) == (0, "sk-123\n", "")


def test_errors_exit_nonzero_with_a_message_on_stderr(home: Path) -> None:
    result = run(home, "key", "get", "google/work")
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("akie: error:")


def test_usage_errors_exit_with_2(home: Path) -> None:
    assert run(home, "key").returncode == 2


def test_help_lists_the_key_group(home: Path) -> None:
    result = run(home, "--help")
    assert result.returncode == 0
    assert "key" in result.stdout
