# akie

A small local store for API keys. The name comes from **API key**.

akie only does two things: `add` a key and `get` it back. Keys live in a local
directory on your machine.

## Command line

```bash
akie key add google/work                  # prompts for the value (no echo)
pass show google | akie key add google/work
akie key add google/work --on-duplicate overwrite

akie key get google/work
```

The value is never a command-line argument. See [docs/cli.md](docs/cli.md).

## Library

```python
from akie import KeyStore, OnDuplicate

keys = KeyStore()
keys.add("google/work", "sk-...")  # raises KeyExists if it exists
keys.add("google/work", "sk-...", on_duplicate=OnDuplicate.IGNORE)
keys.get("google/work")
```

Key names are `<domain>/<slug>`. The store lives in `$AKIE_HOME`, or
`${XDG_DATA_HOME:-~/.local/share}/akie` if that is unset.

See [docs/design.md](docs/design.md) for the design decisions.

## Scope

| | |
|---|---|
| MVP | `akie key add`, `akie key get` |
| Later | `del`, presets |
| Out of scope, permanently | Sharing or syncing keys between machines |

Sharing is deliberately not part of akie. If you want keys on another machine,
move the local directory yourself with whatever fits your setup.

Keys are **not encrypted**. They are protected only by file permissions
(directories `700`, files `600`).

## Development

```bash
uv sync
uv run ruff check
uv run ruff format --check
uv run pytest
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
