"""Command-line interface for b45."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from .core import decode, encode

_EXAMPLES = """examples:
  b45 encode "Hello World"
  b45 decode "+HELLO +WORLD"
  printf 'Hello World' | b45 encode
  printf '+HELLO +WORLD' | b45 decode
"""


def main(argv: Sequence[str] | None = None) -> int:
    """Run the b45 command-line interface."""

    return _run(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def _run(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    text = args.text if args.text is not None else stdin.read()

    if args.command == "encode":
        print(encode(text), file=stdout)
        return 0

    try:
        result = decode(text)
    except ValueError as exc:
        print(f"b45: decode error: {exc}", file=stderr)
        return 1

    print(result, file=stdout)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="b45",
        description="Encode and decode b45 QR Alphanumeric text.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="{encode,decode}",
        required=True,
    )

    for command in ("encode", "decode"):
        subparser = subparsers.add_parser(
            command,
            help=f"{command} b45 text",
            description=f"{command.capitalize()} b45 text. Reads from stdin when TEXT is omitted.",
        )
        subparser.add_argument(
            "text",
            metavar="TEXT",
            nargs="?",
            help="text to process; reads from stdin when omitted",
        )

    return parser


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
