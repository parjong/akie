"""Exception types. Defined here so every layer can raise them."""


class AkieError(Exception):
    """Base class of every error akie raises on purpose."""


class InvalidKeyName(AkieError):
    """The key name is not of the form ``<domain>/<slug>``."""


class KeyExists(AkieError):
    """The key already exists and the duplicate policy is ``OnDuplicate.ERROR``."""


class KeyNotFound(AkieError):
    """The key does not exist."""


class ManifestError(AkieError):
    """The akie home or its ``manifest.toml`` is missing, invalid or unsupported."""


class HomeError(AkieError):
    """The akie home location cannot be determined from the environment."""
