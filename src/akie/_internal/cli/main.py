"""``akie key add`` and ``akie key get``.

The CLI only uses the public API (``from akie import ...``), so whatever it can
do, a library user can do too.
"""

import argparse
import getpass
import sys
from collections.abc import Sequence

from akie import AkieError, KeyStore, OnDuplicate

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2  # argparse exits with 2 itself
EXIT_INTERRUPTED = 130


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="akie", description="A small local store for API keys."
    )
    groups = parser.add_subparsers(dest="group", required=True, metavar="GROUP")

    key = groups.add_parser("key", help="manage keys")
    actions = key.add_subparsers(dest="action", required=True, metavar="ACTION")

    add = actions.add_parser(
        "add",
        help="store a key; the value is read from stdin or prompted for",
        description=(
            "Store a key. The value is never taken from the command line: it is "
            "read from stdin when piped, or prompted for (without echo) on a "
            "terminal."
        ),
    )
    add.add_argument("name", help="key name, <domain>/<slug>")
    add.add_argument(
        "--on-duplicate",
        choices=[policy.value for policy in OnDuplicate],
        default=OnDuplicate.ERROR.value,
        help="what to do if the key exists (default: %(default)s)",
    )

    get = actions.add_parser("get", help="print a key's value")
    get.add_argument("name", help="key name, <domain>/<slug>")
    return parser


def _read_value(name: str) -> str:
    if sys.stdin.isatty():
        return getpass.getpass(f"Value for {name}: ")
    value = sys.stdin.read()
    # Drop exactly one trailing newline, so `echo sk-123 | akie ...` stores sk-123.
    if value.endswith("\r\n"):
        return value[:-2]
    if value.endswith("\n"):
        return value[:-1]
    return value


def _run(args: argparse.Namespace) -> None:
    keys = KeyStore()
    if args.action == "add":
        value = _read_value(args.name)
        if not value:
            raise AkieError("refusing to store an empty value")
        keys.add(args.name, value, on_duplicate=OnDuplicate(args.on_duplicate))
    else:
        sys.stdout.write(keys.get(args.name) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _run(args)
    except AkieError as error:
        print(f"akie: error: {error}", file=sys.stderr)
        return EXIT_ERROR
    except EOFError:
        print("akie: error: no value given", file=sys.stderr)
        return EXIT_ERROR
    except OSError as error:
        print(f"akie: error: {error}", file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        return EXIT_INTERRUPTED
    return EXIT_OK
