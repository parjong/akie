# Design

akie is a small local store for API keys. This document records the decisions
the implementation follows.

## Scope

| | |
|---|---|
| MVP | `key add`, `key get` |
| Later | `key del`, presets |
| Out of scope, permanently | Sharing or syncing keys between machines |

Sharing is not a roadmap item. How a local directory gets to another machine is
the user's concern.

## Key names

`<domain>/<slug>`, nothing else.

- `domain` and `slug` each match `[a-z0-9][a-z0-9._-]{0,63}`; there is exactly
  one `/`.
- Lowercase only: names must not collide on case-insensitive file systems
  (for example when a WSL directory is reached from Windows).
- The first character is alphanumeric, so a name can never be `..` or a hidden
  file. This is also what keeps names clear of akie's `.tmp-*` scratch files.
- The 64-character limit keeps names within file system limits so a long name
  fails validation instead of failing inside the operating system.

## Storage location

1. `$AKIE_HOME` if set. It must be an absolute path.
2. Otherwise `${XDG_DATA_HOME:-~/.local/share}/akie`.

Empty values count as unset. A relative `XDG_DATA_HOME` is ignored, as the XDG
specification requires.

## Layout

```text
$AKIE_HOME/                  # 700
├── manifest.toml            # 600
└── keys/                    # 700
    └── <domain>/            # 700
        └── <slug>           # 600, the value verbatim
```

One file per key; the value is stored as UTF-8 exactly as given, with no
trailing newline added or removed. Keys are **not encrypted**. The only
protection is file permissions.

`keys/` is a subdirectory so that `presets/` can sit next to it later. It is
created when needed.

## Manifest

```toml
version = 1
storage_engine = "local"
```

The manifest records which storage engine owns the directory so the engine can
be replaced later. Unknown versions, unknown storage engines and unknown keys
are errors. Only `local` exists.

- The first `add` creates the directory and the manifest. There is no `init`.
- If the directory exists, has other content and has no manifest, akie refuses
  to use it.
- Reading (`get`) never creates anything. Without a manifest it is an error.

## Behavior of `add`

`on_duplicate` decides what happens when the key exists:

| `OnDuplicate` | Result |
|---|---|
| `ERROR` (default) | raise `KeyExists`; the stored value is untouched |
| `IGNORE` | do nothing and succeed; the stored value is untouched |
| `OVERWRITE` | replace the value |

The library takes the enum and rejects strings. Strings only appear at the CLI
boundary.

Writes are crash-safe: a new key is created exclusively (`O_EXCL`, mode `600`)
and a partial file is removed if writing fails; an overwrite writes a scratch
file in the same directory and `rename`s it over the key.

Known limitation: a reader can observe a freshly created key before its value
has been written, because creation is exclusive but not atomic. Overwrites are
atomic.

## Public API

```python
from akie import KeyStore, OnDuplicate
from akie import AkieError, InvalidKeyName, KeyExists, KeyNotFound

keys = KeyStore()
keys.add("google/work", "sk-...")
keys.add("google/work", "sk-...", on_duplicate=OnDuplicate.IGNORE)
keys.get("google/work")
```

- Compatibility is promised only for what `akie.__all__` lists. Everything
  under `akie._internal` can change at any time.
- `KeyStore()` takes no arguments. The location is controlled by `AKIE_HOME`.
- `KeyStore()` validates an existing manifest but creates nothing.
- Keys and presets will be separate classes (`KeyStore`, later `PresetStore`).
  `PresetStore` is not reserved before it exists.
- The storage contract (`StorageEngine`) is internal. If it is ever exposed,
  an optional argument can be added without breaking anyone.
- If more public modules are needed later, add them next to the top-level API.
  Names already exported from `akie` stay exported.

## Package layout

```text
src/akie/
├── __init__.py          # the public API: re-exports and __all__ only
└── _internal/           # private
    ├── core/            # errors, OnDuplicate, key names, home resolution
    ├── storage/         # manifest, StorageEngine, local engine
    └── service/         # KeyStore
```

Dependencies only point downward: `service → storage → core`. A test enforces
it. The CLI (added separately) is a client of the public API only.

The boundary is expressed with a single private directory and a re-exporting
`__init__.py`. The alternatives considered were underscore-prefixed files,
`api/` + `internal/`, `public/` + `internal/`, `api/` + `_internal/`, no
distinction at all, and separate distributions. The chosen layout gives the
strongest control over the public surface (new internals cannot become public
by accident, and tools hide underscore names) while still showing the layers in
the directory structure. Python cannot enforce the boundary; it is a promise.
`ruff`'s `PLC2701` rule is enabled so that tests of the public API cannot import
`akie._internal`.

## Roadmap

1. `key del`
2. Presets (`PresetStore`, `akie preset ...`)
