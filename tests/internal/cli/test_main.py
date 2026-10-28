import io
from pathlib import Path

import pytest

from akie._internal.cli.main import main


class FakeTerminal(io.StringIO):
    def isatty(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "akie"
    monkeypatch.setenv("AKIE_HOME", str(path))
    return path


def feed(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(text))


def add(monkeypatch: pytest.MonkeyPatch, name: str, value: str, *options: str) -> int:
    feed(monkeypatch, value)
    return main(["key", "add", name, *options])


def test_add_then_get_prints_the_value_and_a_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert add(monkeypatch, "google/work", "sk-123\n") == 0
    assert main(["key", "get", "google/work"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "sk-123\n"
    assert captured.err == ""


@pytest.mark.parametrize(
    ("given", "stored"),
    [
        ("sk-123\n", "sk-123"),
        ("sk-123", "sk-123"),
        ("sk-123\r\n", "sk-123"),
        ("sk-123\n\n", "sk-123\n"),
        ("  padded  \n", "  padded  "),
    ],
)
def test_exactly_one_trailing_newline_is_dropped(
    monkeypatch: pytest.MonkeyPatch, given: str, stored: str
) -> None:
    from akie import KeyStore

    assert add(monkeypatch, "a/b", given) == 0
    assert KeyStore().get("a/b") == stored


def test_value_is_prompted_without_echo_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    prompts: list[str] = []

    def fake_getpass(prompt: str) -> str:
        prompts.append(prompt)
        return "typed-secret"

    monkeypatch.setattr("sys.stdin", FakeTerminal())
    monkeypatch.setattr("getpass.getpass", fake_getpass)
    assert main(["key", "add", "a/b"]) == 0
    assert prompts == ["Value for a/b: "]
    assert main(["key", "get", "a/b"]) == 0
    assert capsys.readouterr().out == "typed-secret\n"


def test_duplicate_is_an_error_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert add(monkeypatch, "a/b", "old") == 0
    assert add(monkeypatch, "a/b", "new") == 1
    assert "already exists" in capsys.readouterr().err
    assert main(["key", "get", "a/b"]) == 0
    assert capsys.readouterr().out == "old\n"


def test_on_duplicate_ignore_keeps_the_old_value(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    add(monkeypatch, "a/b", "old")
    assert add(monkeypatch, "a/b", "new", "--on-duplicate", "ignore") == 0
    main(["key", "get", "a/b"])
    assert capsys.readouterr().out == "old\n"


def test_on_duplicate_overwrite_replaces_the_value(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    add(monkeypatch, "a/b", "old")
    assert add(monkeypatch, "a/b", "new", "--on-duplicate", "overwrite") == 0
    main(["key", "get", "a/b"])
    assert capsys.readouterr().out == "new\n"


def test_unknown_on_duplicate_is_a_usage_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    feed(monkeypatch, "x")
    with pytest.raises(SystemExit) as raised:
        main(["key", "add", "a/b", "--on-duplicate", "merge"])
    assert raised.value.code == 2


def test_the_value_cannot_be_given_as_an_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    feed(monkeypatch, "x")
    with pytest.raises(SystemExit) as raised:
        main(["key", "add", "a/b", "sk-on-the-command-line"])
    assert raised.value.code == 2


@pytest.mark.parametrize("argv", [[], ["key"], ["nope"], ["key", "nope"]])
def test_missing_or_unknown_commands_are_usage_errors(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main(argv)
    assert raised.value.code == 2


def test_an_empty_value_is_refused_and_nothing_is_created(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], home: Path
) -> None:
    assert add(monkeypatch, "a/b", "") == 1
    assert add(monkeypatch, "a/b", "\n") == 1
    assert "empty value" in capsys.readouterr().err
    assert not home.exists()


def test_invalid_name_is_an_error_not_a_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert add(monkeypatch, "Bad/Name", "x") == 1
    assert main(["key", "get", "nodomain"]) == 1
    err = capsys.readouterr().err
    assert err.count("akie: error: invalid key name") == 2


def test_get_missing_key_is_an_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    add(monkeypatch, "a/b", "x")
    assert main(["key", "get", "a/c"]) == 1
    assert "akie: error: no such key: a/c" in capsys.readouterr().err


def test_get_on_a_fresh_home_is_an_error_and_creates_nothing(
    capsys: pytest.CaptureFixture[str], home: Path
) -> None:
    assert main(["key", "get", "a/b"]) == 1
    assert "not an akie home" in capsys.readouterr().err
    assert not home.exists()


def test_eof_at_the_prompt_is_an_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def raise_eof(prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("sys.stdin", FakeTerminal())
    monkeypatch.setattr("getpass.getpass", raise_eof)
    assert main(["key", "add", "a/b"]) == 1
    assert "no value given" in capsys.readouterr().err


def test_os_errors_are_reported_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    monkeypatch.setenv("AKIE_HOME", str(blocker / "akie"))
    assert add(monkeypatch, "a/b", "x") == 1
    assert capsys.readouterr().err.startswith("akie: error:")
