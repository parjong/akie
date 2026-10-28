# Command line

```text
akie key add NAME [--on-duplicate {error,ignore,overwrite}]
akie key get NAME
```

`NAME` is `<domain>/<slug>`, for example `google/work`. See
[design.md](design.md) for the naming rules.

Where keys are stored is controlled by `AKIE_HOME`, else
`${XDG_DATA_HOME:-~/.local/share}/akie`.

## `key add`

Stores a key. **The value is never a command-line argument**, so it cannot end up
in shell history or in `ps` output. It comes from:

- **stdin**, when stdin is not a terminal. Exactly one trailing newline is
  dropped, so `echo sk-123 | akie key add google/work` stores `sk-123`.
- **a prompt without echo**, when stdin is a terminal.

```bash
akie key add google/work                       # prompts for the value
pass show google | akie key add google/work    # or pipe it in
akie key add google/work --on-duplicate overwrite
```

If the key already exists, `--on-duplicate` decides:

| value | result |
|---|---|
| `error` (default) | fail; the stored value is untouched |
| `ignore` | do nothing and succeed; the stored value is untouched |
| `overwrite` | replace the value |

An empty value is refused. A success prints nothing.

## `key get`

Prints the value followed by a newline on stdout.

```bash
akie key get google/work
export GOOGLE_API_KEY="$(akie key get google/work)"
```

Command substitution removes the trailing newline. Reading never creates
anything: on a machine where nothing has been added yet, `get` fails.

## Exit status

| status | meaning |
|---|---|
| `0` | success |
| `1` | an error: invalid name, key exists, key not found, empty value, an unusable akie home, a file system error. The message is on stderr as `akie: error: ...` |
| `2` | wrong usage (unknown command, missing argument, bad option value) |
| `130` | interrupted |

Keys are **not encrypted**. They are protected only by file permissions
(directories `700`, files `600`).

## Known limitation

The name is validated when the key is stored, after the value has been read. On a
terminal you may therefore type a value before learning that the name is invalid.
