# akie

A small local store for API keys. The name comes from **API key**.

akie only does two things: `add` a key and `get` it back. Keys live in a local
directory on your machine.

> Status: bootstrapping. The commands and the library API are not implemented
> yet.

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
