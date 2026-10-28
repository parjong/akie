import pytest

from akie._internal.core.errors import InvalidKeyName
from akie._internal.core.name import KeyName


def test_parse_splits_domain_and_slug() -> None:
    name = KeyName.parse("google/work")
    assert (name.domain, name.slug) == ("google", "work")
    assert str(name) == "google/work"


@pytest.mark.parametrize(
    "text", ["a/b", "0/0", "github/ci", "my-svc/key_1.v2", "a" * 64 + "/" + "b" * 64]
)
def test_parse_accepts_valid_names(text: str) -> None:
    assert str(KeyName.parse(text)) == text


@pytest.mark.parametrize(
    "text",
    [
        "",
        "google",
        "google/",
        "/work",
        "google/work/extra",
        "Google/work",
        "google/Work",
        "../work",
        "google/..",
        ".hidden/work",
        "google/.hidden",
        "-a/b",
        "google/work\n",
        "google/wor k",
        "google/wörk",
        "a" * 65 + "/b",
        "a/" + "b" * 65,
    ],
)
def test_parse_rejects_invalid_names(text: str) -> None:
    with pytest.raises(InvalidKeyName):
        KeyName.parse(text)


def test_parse_rejects_non_str() -> None:
    with pytest.raises(TypeError):
        KeyName.parse(b"google/work")  # type: ignore[arg-type]
