import akie

EXPECTED = {
    "AkieError",
    "InvalidKeyName",
    "KeyExists",
    "KeyNotFound",
    "KeyStore",
    "OnDuplicate",
}


def test_public_api_is_exactly_the_documented_set() -> None:
    # Growing the public surface must be a deliberate change to this test.
    assert set(akie.__all__) == EXPECTED


def test_every_public_name_is_importable() -> None:
    for name in akie.__all__:
        assert hasattr(akie, name)


def test_exceptions_share_a_base_class() -> None:
    for name in ("InvalidKeyName", "KeyExists", "KeyNotFound"):
        assert issubclass(getattr(akie, name), akie.AkieError)
